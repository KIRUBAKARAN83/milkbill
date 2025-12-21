from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum

PRICE_PER_LITRE = Decimal(getattr(settings, 'PRICE_PER_LITRE', 50.0))


class Customer(models.Model):
    name = models.CharField(max_length=200)
    balance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # ✅ THIS IS WHAT YOUR VIEWS EXPECT
    def recalculate_balance(self):
        total_ml = (
            self.milk_entries
            .aggregate(total=Sum('quantity_ml'))
            .get('total') or 0
        )

        litres = Decimal(total_ml) / Decimal('1000')
        self.balance_amount = litres * PRICE_PER_LITRE
        self.save(update_fields=['balance_amount'])


class MilkEntry(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='milk_entries'
    )
    date = models.DateField(default=timezone.now)
    quantity_ml = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    @property
    def litres(self):
        return Decimal(self.quantity_ml) / Decimal('1000')

    @property
    def amount(self):
        return self.litres * PRICE_PER_LITRE

    def __str__(self):
        return f"{self.customer.name} - {self.date} - {self.quantity_ml} ml"
