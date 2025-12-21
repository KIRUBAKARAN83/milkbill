from django import forms
from .models import Customer, MilkEntry


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
                'step': '0.01'
            }),
        }


class MilkEntryForm(forms.ModelForm):
    customer_name = forms.CharField(required=False)

    class Meta:
        model = MilkEntry
        fields = ['customer', 'customer_name', 'date', 'quantity_ml']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].required = False

    def clean(self):
        cleaned = super().clean()
        customer = cleaned.get('customer')
        name = cleaned.get('customer_name')

        if name:
            cleaned['customer_name'] = name.strip()

        if not customer and not cleaned.get('customer_name'):
            raise forms.ValidationError(
                "Select a customer or enter a new customer name."
            )

        if customer and cleaned.get('customer_name'):
            raise forms.ValidationError(
                "Choose only one: customer OR new customer."
            )

        return cleaned
