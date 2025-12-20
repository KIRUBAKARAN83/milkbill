from django import forms
from .models import Customer, MilkEntry


class CustomerForm(forms.ModelForm):
    """
    Customer name only.
    Balance is calculated automatically.
    """
    class Meta:
        model = Customer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name',
                'autocomplete': 'off'
            }),
        }


class MilkEntryForm(forms.ModelForm):
    customer_name = forms.CharField(
        required=False,
        label='New Customer (optional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type new customer name'
        })
    )

    class Meta:
        model = MilkEntry
        fields = ['customer', 'customer_name', 'date', 'quantity_ml']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'quantity_ml': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].required = False

    def clean(self):
        cleaned = super().clean()
        customer = cleaned.get('customer')
        name = cleaned.get('customer_name')
        qty = cleaned.get('quantity_ml')

        if not customer and not name:
            raise forms.ValidationError(
                "Select an existing customer or enter a new name."
            )

        if qty is None or qty < 0:
            raise forms.ValidationError("Quantity must be 0 or greater.")

        return cleaned
