from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

from .models import Customer, MilkEntry, PRICE_PER_LITRE
from .forms import MilkEntryForm, CustomerForm
from .pdf_generation import generate_bill_pdf



# Dashboard
# ...existing code...


@login_required(login_url='login')
def home(request):
    try:
        total_customers = Customer.objects.count()
        total_ml = MilkEntry.objects.aggregate(total=Sum('quantity_ml'))['total'] or 0
        total_litres = round(Decimal(total_ml) / Decimal(1000), 2) if total_ml else Decimal(0)
        # total amount across all customers / entries
        total_amount = round((Decimal(total_ml) / Decimal(1000)) * Decimal(PRICE_PER_LITRE), 2) if total_ml else Decimal(0)
        total_balance = Customer.objects.aggregate(balance=Sum('balance_amount'))['balance'] or Decimal(0)
        last_entries = MilkEntry.objects.select_related('customer').order_by('-date')[:10]
        context = {
            'total_customers': total_customers,
            'total_litres': total_litres,
            'total_balance': round(total_balance, 2),
            'total_amount': total_amount,
            'last_entries': last_entries,
        }
        return render(request, 'accounts/home.html', context)
    except Exception as e:
        return render(request, 'accounts/home.html', {
            'total_customers': 0,
            'total_litres': 0,
            'total_balance': 0,
            'total_amount': 0,
            'last_entries': [],
            'error': str(e)
        })
# ...existing code...

@login_required(login_url='login')
def customer_list(request):
    customers = Customer.objects.all()
    for customer in customers:
        total_ml = MilkEntry.objects.filter(customer=customer).aggregate(total=Sum('quantity_ml'))['total'] or 0
        customer.total_ml = total_ml
        customer.total_litres = round(Decimal(total_ml) / Decimal(1000), 2) if total_ml else Decimal(0)
    return render(request, 'accounts/customer_list.html', {'customers': customers})

@login_required(login_url='login')
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    entries = MilkEntry.objects.filter(customer=customer).order_by('-date')
    
    months_data = {}
    for entry in entries:
        key = (entry.date.year, entry.date.month)
        if key not in months_data:
            months_data[key] = {
                'year': entry.date.year,
                'month': entry.date.month,
                'month_name': entry.date.strftime('%B %Y'),
                'entries': [],
                'total_ml': 0,
                'total_litres': Decimal(0),
                'total_amount': Decimal(0),
            }
        months_data[key]['entries'].append(entry)
        months_data[key]['total_ml'] += entry.quantity_ml
        months_data[key]['total_amount'] += entry.amount
    
    for month_key in months_data:
        ml = months_data[month_key]['total_ml']
        months_data[month_key]['total_litres'] = round(Decimal(ml) / Decimal(1000), 2)
        months_data[month_key]['total_amount'] = round(months_data[month_key]['total_amount'], 2)
    
    sorted_months = sorted(months_data.values(), key=lambda x: (x['year'], x['month']), reverse=True)
    
    context = {
        'customer': customer,
        'months_data': sorted_months,
        'total_entries': entries.count(),
    }
    return render(request, 'accounts/customer_detail.html', context)

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def add_entry(request):
    if request.method == 'POST':
        form = MilkEntryForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data.get('customer')
            new_name = form.cleaned_data.get('customer_name')
            
            if not customer and new_name:
                customer, created = Customer.objects.get_or_create(
                    name=new_name.strip()
                )
            
            if customer:
                entry = MilkEntry.objects.create(
                    customer=customer,
                    date=form.cleaned_data['date'],
                    quantity_ml=form.cleaned_data['quantity_ml']
                )
                return redirect('accounts:customer_list')
    else:
        form = MilkEntryForm()
    
    return render(request, 'accounts/entry_form.html', {'form': form})

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def edit_entry(request, entry_id):
    entry = get_object_or_404(MilkEntry, id=entry_id)
    if request.method == 'POST':
        form = MilkEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('accounts:customer_detail', customer_id=entry.customer.id)
    else:
        form = MilkEntryForm(instance=entry)
    return render(request, 'accounts/entry_form.html', {'form': form, 'title': 'Edit Milk Entry'})

@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_entry(request, entry_id):
    entry = get_object_or_404(MilkEntry, id=entry_id)
    customer_id = entry.customer.id
    entry.delete()
    return redirect('accounts:customer_detail', customer_id=customer_id)

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('accounts:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'accounts/customer_form.html', {'form': form, 'customer': customer, 'title': 'Edit Customer'})

@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect('accounts:customer_list')

@login_required(login_url='login')
def chart_data(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    entries = MilkEntry.objects.filter(customer=customer).order_by('date')[:30]
    labels = [e.date.strftime('%Y-%m-%d') for e in entries]
    data = [float(e.litres) for e in entries]
    return JsonResponse({'labels': labels, 'data': data})

@login_required(login_url='login')
def bill_pdf(request, customer_id, year=None, month=None):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if year and month:
        entries = MilkEntry.objects.filter(
            customer=customer,
            date__year=year,
            date__month=month
        ).order_by('date')
        filename = f"bill_{customer.name.replace(' ', '_')}_{year}_{month:02d}"
    else:
        entries = MilkEntry.objects.filter(customer=customer).order_by('date')
        filename = f"bill_{customer.name.replace(' ', '_')}_all"
    
    total_ml = entries.aggregate(total=Sum('quantity_ml'))['total'] or 0
    total_litres = round(Decimal(total_ml) / Decimal(1000), 2) if total_ml else Decimal(0)
    total_amount = round((Decimal(total_ml) / Decimal(1000)) * Decimal(PRICE_PER_LITRE), 2) if total_ml else Decimal(0)
    
    pdf_buffer = generate_bill_pdf(
        customer=customer,
        entries=entries,
        total_ml=total_ml,
        total_litres=total_litres,
        total_amount=total_amount,
        price_per_litre=PRICE_PER_LITRE,
        year=year,
        month=month
    )
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required(login_url='login')
def monthly_summary(request):
    today = timezone.localdate()
    start_date = today.replace(day=1)
    if today.month == 12:
        end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    entries = MilkEntry.objects.filter(date__range=[start_date, end_date]).select_related('customer')
    summary = {}
    for entry in entries:
        cid = entry.customer.id
        if cid not in summary:
            summary[cid] = {'name': entry.customer.name, 'total_ml': 0, 'amount': Decimal(0)}
        summary[cid]['total_ml'] += entry.quantity_ml
        summary[cid]['amount'] += entry.amount
    
    summary_list = []
    for data in summary.values():
        litres = round(Decimal(data['total_ml']) / Decimal(1000), 2)
        amt = round(data['amount'], 2)
        summary_list.append({'name': data['name'], 'total_ml': data['total_ml'], 'litres': litres, 'amount': amt})
    
    total_amount = round(sum(item['amount'] for item in summary_list), 2)
    return render(request, 'accounts/monthly_summary.html', {
        'summary': summary_list,
        'total_amount': total_amount,
        'start': start_date,
        'end': end_date,
    })
