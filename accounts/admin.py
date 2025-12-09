from django.contrib import admin
from .models import Customer, MilkEntry

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'whatsapp_number', 'created_at')
    search_fields = ('name', 'phone', 'whatsapp_number')

@admin.register(MilkEntry)
class MilkEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'quantity_ml', 'litres_display', 'amount_display')
    list_filter = ('date', 'customer')
    search_fields = ('customer__name',)
    ordering = ('-date',)

    def litres_display(self, obj):
        return f"{obj.litres:.3f}"
    litres_display.short_description = 'Litres'

    def amount_display(self, obj):
        return f"₹{obj.amount:.2f}"
    amount_display.short_description = 'Amount'