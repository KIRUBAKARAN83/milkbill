from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),
    

    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),

    # Bill PDF
    path('customers/<int:customer_id>/bill-pdf/', views.bill_pdf, name='bill_pdf'),
    path('customers/<int:customer_id>/bill-pdf/<int:year>/<int:month>/', views.bill_pdf, name='bill_pdf_month'),

    # Chart data
    path('customers/<int:customer_id>/chart-data/', views.chart_data, name='chart_data'),

    # Milk Entry Management
    path('entry/add/', views.add_entry, name='add_entry'),
    path('entry/<int:entry_id>/edit/', views.edit_entry, name='edit_entry'),
    path('entry/<int:entry_id>/delete/', views.delete_entry, name='delete_entry'),

    # Reports
    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),
]
