from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

PRICE_PER_LITRE = getattr(settings, 'PRICE_PER_LITRE', 50.0)

class Customer(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name or "Unknown Customer"

    class Meta:
        ordering = ['-created_at']


class MilkEntry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='milk_entries')
    date = models.DateField(default=timezone.now)
    quantity_ml = models.IntegerField(default=0)  # quantity in ml
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @property
    def litres(self):
        """Convert ml to litres"""
        return Decimal(self.quantity_ml) / Decimal(1000)

    @property
    def amount(self):
        """Calculate amount based on litres"""
        return self.litres * Decimal(PRICE_PER_LITRE)

    def __str__(self):
        return f"{self.customer.name} - {self.date} - {self.quantity_ml}ml"

    class Meta:
        ordering = ['-date']
