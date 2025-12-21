from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required

from .models import Customer, MilkEntry, PRICE_PER_LITRE
from .forms import MilkEntryForm, CustomerForm
from .pdf_generation import generate_bill_pdf


@login_required(login_url='login')
def home(request):
    total_customers = Customer.objects.count()
    total_ml = MilkEntry.objects.aggregate(total=Sum('quantity_ml'))['total'] or 0

    total_litres = round(Decimal(total_ml) / Decimal(1000), 2)
    total_amount = round(total_litres * Decimal(PRICE_PER_LITRE), 2)
    total_balance = Customer.objects.aggregate(balance=Sum('balance_amount'))['balance'] or Decimal(0)

    last_entries = MilkEntry.objects.select_related('customer').order_by('-date')[:10]

    return render(request, 'accounts/home.html', {
        'total_customers': total_customers,
        'total_litres': total_litres,
        'total_amount': total_amount,
        'total_balance': round(total_balance, 2),
        'last_entries': last_entries,
    })


@login_required(login_url='login')
def customer_list(request):
    customers = Customer.objects.all()
    for customer in customers:
        total_ml = MilkEntry.objects.filter(customer=customer).aggregate(total=Sum('quantity_ml'))['total'] or 0
        customer.total_litres = round(Decimal(total_ml) / Decimal(1000), 2)
    return render(request, 'accounts/customer_list.html', {'customers': customers})


@login_required(login_url='login')
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    entries = MilkEntry.objects.filter(customer=customer).order_by('-date')

    return render(request, 'accounts/customer_detail.html', {
        'customer': customer,
        'entries': entries,
        'total_entries': entries.count()
    })


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def add_entry(request):
    if request.method == 'POST':
        form = MilkEntryForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data.get('customer')
            new_name = form.cleaned_data.get('customer_name')

            if not customer and new_name:
                customer, _ = Customer.objects.get_or_create(name=new_name.strip())

            MilkEntry.objects.create(
                customer=customer,
                date=form.cleaned_data['date'],
                quantity_ml=form.cleaned_data['quantity_ml']
            )
            return redirect('accounts:customer_list')
    else:
        form = MilkEntryForm()

    return render(request, 'accounts/entry_form.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_entry(request, entry_id):
    entry = get_object_or_404(MilkEntry, id=entry_id)
    cid = entry.customer.id
    entry.delete()
    return redirect('accounts:customer_detail', customer_id=cid)


@login_required(login_url='login')
def chart_data(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    entries = MilkEntry.objects.filter(customer=customer).order_by('date')[:30]

    return JsonResponse({
        'labels': [e.date.strftime('%Y-%m-%d') for e in entries],
        'data': [float(e.litres) for e in entries],
    })


@login_required(login_url='login')
def bill_pdf(request, customer_id, year=None, month=None):
    customer = get_object_or_404(Customer, id=customer_id)

    if year and month:
        entries = MilkEntry.objects.filter(
            customer=customer,
            date__year=year,
            date__month=month
        )
        filename = f"bill_{customer.name}_{year}_{month}"
    else:
        entries = MilkEntry.objects.filter(customer=customer)
        filename = f"bill_{customer.name}_all"

    total_ml = entries.aggregate(total=Sum('quantity_ml'))['total'] or 0
    total_litres = Decimal(total_ml) / Decimal(1000)
    total_amount = total_litres * Decimal(PRICE_PER_LITRE)

    pdf = generate_bill_pdf(
        customer,
        entries,
        total_ml,
        total_litres,
        total_amount,
        PRICE_PER_LITRE,
        year,
        month
    )

    response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response


@login_required(login_url='login')
def monthly_summary(request):
    today = timezone.localdate()
    start_date = today.replace(day=1)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    entries = MilkEntry.objects.filter(date__range=[start_date, end_date]).select_related('customer')

    summary = {}
    for entry in entries:
        cid = entry.customer.id
        summary.setdefault(cid, {
            'name': entry.customer.name,
            'total_ml': 0,
            'amount': Decimal(0)
        })
        summary[cid]['total_ml'] += entry.quantity_ml
        summary[cid]['amount'] += entry.amount

    summary_list = []
    for s in summary.values():
        litres = round(Decimal(s['total_ml']) / Decimal(1000), 2)
        summary_list.append({
            'name': s['name'],
            'total_ml': s['total_ml'],
            'litres': litres,
            'amount': round(s['amount'], 2)
        })

    total_amount = round(sum(i['amount'] for i in summary_list), 2)

    return render(request, 'accounts/monthly_summary.html', {
        'summary': summary_list,
        'total_amount': total_amount,
        'start': start_date,
        'end': end_date,
    })
