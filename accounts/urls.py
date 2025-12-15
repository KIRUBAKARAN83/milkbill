from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home, name='home'),

    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),

    path('entry/add/', views.add_entry, name='add_entry'),
    path('entry/<int:entry_id>/edit/', views.edit_entry, name='edit_entry'),
    path('entry/<int:entry_id>/delete/', views.delete_entry, name='delete_entry'),
    path('entry/<int:entry_id>/restore/', views.restore_entry, name='restore_entry'),

    path('customers/<int:customer_id>/chart-data/', views.chart_data, name='chart_data'),

    path('customers/<int:customer_id>/bill/', views.bill_pdf, name='bill_pdf'),
    path(
        'customers/<int:customer_id>/bill/<int:year>/<int:month>/',
        views.bill_pdf,
        name='bill_pdf_month'
    ),

    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),
]
