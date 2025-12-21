from django import forms
from .models import Customer, MilkEntry

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'balance_amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'balance_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MilkEntryForm(forms.ModelForm):
    customer_name = forms.CharField(
        required=False,
        label="New Customer",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = MilkEntry
        fields = ['customer', 'customer_name', 'date', 'quantity_ml']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity_ml': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def clean(self):
        cleaned = super().clean()
        customer = cleaned.get("customer")
        customer_name = cleaned.get("customer_name")

        if not customer and not customer_name:
            raise forms.ValidationError(
                "Select existing customer OR enter a new customer name."
            )

        return cleaned
