from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Lower

PRICE_PER_LITRE = Decimal(
    getattr(settings, 'PRICE_PER_LITRE', 50)
)


class Customer(models.Model):
    name = models.CharField(max_length=200)

    # 🔒 Derived field – NEVER manually edited
    balance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_customer_name_ci'
            )
        ]

    def __str__(self):
        return self.name




class MilkEntry(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='milk_entries'
    )

    date = models.DateField(default=timezone.now)
    quantity_ml = models.PositiveIntegerField(default=0)

    # Soft delete (used everywhere)
    is_deleted = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

   
