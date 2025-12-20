from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    # ─────────────────────────
    # DASHBOARD
    # ─────────────────────────
    path('', views.home, name='home'),

    # ─────────────────────────
    # CUSTOMERS
    # ─────────────────────────
    path('customers/', views.customer_list, name='customer_list'),
    path(
        'customers/<int:customer_id>/',
        views.customer_detail,
        name='customer_detail'
    ),

    # ─────────────────────────
    # CHART DATA (AJAX)
    # ─────────────────────────
    path(
        'customers/<int:customer_id>/chart-data/',
        views.chart_data,
        name='chart_data'
    ),

    # ─────────────────────────
    # MILK ENTRIES
    # ─────────────────────────
    path('entry/add/', views.add_entry, name='add_entry'),
    path(
        'entry/<int:entry_id>/edit/',
        views.edit_entry,
        name='edit_entry'
    ),
    path(
        'entry/<int:entry_id>/delete/',
        views.delete_entry,
        name='delete_entry'
    ),
    path(
        'entry/<int:entry_id>/restore/',
        views.restore_entry,
        name='restore_entry'
    ),

    # ─────────────────────────
    # BILLS / PDF
    # ─────────────────────────
    path(
        'customers/<int:customer_id>/bill/',
        views.bill_pdf,
        name='bill_pdf'
    ),
    path(
        'customers/<int:customer_id>/bill/<int:year>/<int:month>/',
        views.bill_pdf,
        name='bill_pdf_month'
    ),

    # ─────────────────────────
    # WHATSAPP BILL
    # ─────────────────────────
    path(
        'customers/<int:customer_id>/send-whatsapp/<int:year>/<int:month>/',
        views.send_bill_whatsapp,
        name='send_bill_whatsapp'
    ),

    # ─────────────────────────
    # REPORTS
    # ─────────────────────────
    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),

    # ─────────────────────────
    # FINANCE (SAFE STUBS)
    # ─────────────────────────
   
]
