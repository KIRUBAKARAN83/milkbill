from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal

PRICE_PER_LITRE = Decimal(str(getattr(settings, 'PRICE_PER_LITRE', 50)))

class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MilkEntry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='milk_entries')
    date = models.DateField(default=timezone.now)
    quantity_ml = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def litres(self):
        return Decimal(self.quantity_ml) / Decimal("1000")

    @property
    def amount(self):
        return self.litres * PRICE_PER_LITRE

    def __str__(self):
        return f"{self.customer.name} | {self.date} | {self.quantity_ml}ml"
