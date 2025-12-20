from django import forms
from .models import Customer, MilkEntry
from decimal import Decimal


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'balance_amount']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'balance_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Previous unpaid balance',
                'step': '0.01'
            }),
        }


class MilkEntryForm(forms.ModelForm):
    # Manual customer input
    customer_name = forms.CharField(
        required=False,
        label='New Customer (optional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type new customer name (optional)',
        })
    )

    class Meta:
        model = MilkEntry
        # ⚠️ customer_name REMOVED from Meta.fields
        fields = ['customer', 'date', 'quantity_ml']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'quantity_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '1',
                'placeholder': 'Quantity in ml'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.order_by('name')
        self.fields['customer'].required = False

    def clean(self):
        cleaned = super().clean()

        customer = cleaned.get('customer')
        customer_name = cleaned.get('customer_name')
        quantity = cleaned.get('quantity_ml')

        if not customer and not customer_name:
            raise forms.ValidationError(
                "Select an existing customer or enter a new customer name."
            )

        if quantity is None or quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)

        customer = self.cleaned_data.get('customer')
        customer_name = self.cleaned_data.get('customer_name')

        if not customer:
            customer, _ = Customer.objects.get_or_create(
                name=customer_name.strip()
            )

        instance.customer = customer

        if commit:
            instance.save()

        return instance
