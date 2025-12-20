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
from .whatsapp import send_whatsapp_pdf



# ─────────────────────────────
# DASHBOARD + SEARCH
# ─────────────────────────────
@login_required(login_url='login')
def home(request):
    query = request.GET.get('q', '').strip()
    error = None

    if query:
        qs = Customer.objects.filter(name__icontains=query)
        count = qs.count()

        if count == 1:
            return redirect(
                'accounts:customer_detail',
                customer_id=qs.first().id
            )

        elif count > 1:
            return HttpResponseRedirect(
                f"{reverse('accounts:customer_list')}?q={query}"
            )

        else:
            error = "No customer found"

    total_customers = Customer.objects.count()

    total_ml = (
        MilkEntry.objects
        .filter(is_deleted=False)
        .aggregate(total=Sum('quantity_ml'))
        .get('total') or 0
    )

    total_litres = Decimal(total_ml) / Decimal('1000')
    total_amount = total_litres * Decimal(PRICE_PER_LITRE)

    total_balance = (
        Customer.objects
        .aggregate(balance=Sum('balance_amount'))
        .get('balance') or Decimal('0')
    )

    last_entries = (
        MilkEntry.objects
        .filter(is_deleted=False)
        .select_related('customer')
        .order_by('-date')[:10]
    )

    return render(request, 'accounts/home.html', {
        'error': error,
        'total_customers': total_customers,
        'total_litres': round(total_litres, 2),
        'total_amount': round(total_amount, 2),
        'total_balance': round(total_balance, 2),
        'last_entries': last_entries,
    })

# ─────────────────────────────
# CUSTOMER LIST
# ─────────────────────────────
@login_required(login_url='login')
def customer_list(request):
    customers = Customer.objects.all()
    for customer in customers:
        total_ml = MilkEntry.objects.filter(customer=customer).aggregate(total=Sum('quantity_ml'))['total'] or 0
        customer.total_ml = total_ml
        customer.total_litres = round(Decimal(total_ml) / Decimal(1000), 2) if total_ml else Decimal(0)
    return render(request, 'accounts/customer_list.html', {'customers': customers})

# ─────────────────────────────
# CUSTOMER DETAIL
# ─────────────────────────────
@login_required(login_url='login')
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    entries = MilkEntry.objects.filter(
        customer=customer,
        is_deleted=False
    ).order_by('-date')

    months = {}

    for e in entries:
        key = (e.date.year, e.date.month)
        months.setdefault(key, {
            'year': e.date.year,
            'month': e.date.month,
            'month_name': e.date.strftime('%B %Y'),
            'entries': [],
            'total_ml': 0,
            'total_amount': Decimal('0'),
        })

        months[key]['entries'].append(e)
        months[key]['total_ml'] += e.quantity_ml
        months[key]['total_amount'] += e.amount

    for m in months.values():
        m['total_litres'] = round(Decimal(m['total_ml']) / Decimal('1000'), 2)
        m['total_amount'] = round(m['total_amount'], 2)

    return render(request, 'accounts/customer_detail.html', {
        'customer': customer,
        'months_data': sorted(
            months.values(),
            key=lambda x: (x['year'], x['month']),
            reverse=True
        ),
        'total_entries': entries.count(),
    })

# ─────────────────────────────
# ADD / EDIT ENTRY
# ─────────────────────────────
@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def add_entry(request):
    form = MilkEntryForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        customer = form.cleaned_data.get('customer')
        name = form.cleaned_data.get('customer_name')

        if not customer and name:
            customer, _ = Customer.objects.get_or_create(name=name.strip())

        MilkEntry.objects.create(
            customer=customer,
            date=form.cleaned_data['date'],
            quantity_ml=form.cleaned_data['quantity_ml']
        )

        customer.recalculate_balance()
        return redirect('accounts:customer_list')

    return render(request, 'accounts/entry_form.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def edit_entry(request, entry_id):
    entry = get_object_or_404(MilkEntry, id=entry_id, is_deleted=False)
    form = MilkEntryForm(request.POST or None, instance=entry)

    if request.method == 'POST' and form.is_valid():
        form.save()
        entry.customer.recalculate_balance()
        return redirect('accounts:customer_detail', customer_id=entry.customer.id)

    return render(request, 'accounts/entry_form.html', {'form': form})


# ─────────────────────────────
# DELETE / RESTORE ENTRY
# ─────────────────────────────
@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_entry(request, entry_id):
    entry = get_object_or_404(MilkEntry, id=entry_id, is_deleted=False)
    entry.is_deleted = True
    entry.save()
    entry.customer.recalculate_balance()
    return JsonResponse({'status': 'deleted'})


@login_required(login_url='login')
@require_http_methods(["POST"])
def restore_entry(request, entry_id):
    entry = get_object_or_404(MilkEntry, id=entry_id, is_deleted=True)
    entry.is_deleted = False
    entry.save()
    entry.customer.recalculate_balance()
    return JsonResponse({'status': 'restored'})


# ─────────────────────────────
# ✅ CHART DATA (THIS WAS MISSING)
# ─────────────────────────────
@login_required(login_url='login')
def chart_data(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)

    entries = MilkEntry.objects.filter(
        customer=customer,
        is_deleted=False
    ).order_by('date')

    return JsonResponse({
        'labels': [e.date.strftime('%Y-%m-%d') for e in entries],
        'data': [float(e.litres) for e in entries],
    })



# ─────────────────────────────
# PDF BILL
# ─────────────────────────────
@login_required(login_url='login')
def bill_pdf(request, customer_id, year=None, month=None):
    customer = get_object_or_404(Customer, id=customer_id)

    entries = MilkEntry.objects.filter(customer=customer, is_deleted=False)

    if year and month:
        entries = entries.filter(date__year=year, date__month=month)
        filename = f"bill_{customer.id}_{year}_{month}.pdf"
    else:
        filename = f"bill_{customer.id}_all.pdf"

    total_ml = entries.aggregate(total=Sum('quantity_ml'))['total'] or 0
    total_litres = Decimal(total_ml) / Decimal(1000)
    total_amount = total_litres * Decimal(PRICE_PER_LITRE)

    pdf = generate_bill_pdf(
        customer,
        entries.order_by('date'),
        total_ml,
        total_litres,
        total_amount,
        PRICE_PER_LITRE,
        year,
        month
    )

    response = HttpResponse(pdf.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ─────────────────────────────
# WHATSAPP BILL
# ─────────────────────────────
@login_required(login_url='login')
@require_http_methods(["POST"])
def send_bill_whatsapp(request, customer_id, year, month):
    customer = get_object_or_404(Customer, id=customer_id)

    entries = MilkEntry.objects.filter(
        customer=customer,
        is_deleted=False,
        date__year=year,
        date__month=month
    )

    if not entries.exists():
        return JsonResponse({'error': 'No entries'}, status=400)

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

    path = f"bills/bill_{customer.id}_{year}_{month}.pdf"
    saved = default_storage.save(path, ContentFile(pdf.getvalue()))
    pdf_url = request.build_absolute_uri(settings.MEDIA_URL + saved)

    send_whatsapp_pdf(
        phone_number="whatsapp:+9677815162",
        pdf_url=pdf_url,
        message=f"Hello {customer.name}, your milk bill is attached."
    )

    return JsonResponse({'status': 'sent'})


# ─────────────────────────────
# MONTHLY SUMMARY
# ─────────────────────────────
@login_required(login_url='login')
def monthly_summary(request):
    today = timezone.localdate()
    start = today.replace(day=1)
    end = (
        today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        if today.month < 12 else
        today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    )

    entries = MilkEntry.objects.filter(
        date__range=[start, end],
        is_deleted=False
    ).select_related('customer')

    summary = {}

    for e in entries:
        summary.setdefault(e.customer.id, {
            'name': e.customer.name,
            'total_ml': 0,
            'amount': Decimal(0)
        })
        summary[e.customer.id]['total_ml'] += e.quantity_ml
        summary[e.customer.id]['amount'] += e.amount

    summary_list = [{
        'name': s['name'],
        'total_ml': s['total_ml'],
        'litres': round(Decimal(s['total_ml']) / Decimal(1000), 2),
        'amount': round(s['amount'], 2)
    } for s in summary.values()]

    return render(request, 'accounts/monthly_summary.html', {
        'summary': summary_list,
        'total_amount': round(sum(i['amount'] for i in summary_list), 2),
        'start': start,
        'end': end
    })


# ─────────────────────────────
