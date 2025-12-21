from django import forms
from .models import Customer, MilkEntry


# ─────────────────────────────────────
# CUSTOMER FORM
# ─────────────────────────────────────

class CustomerForm(forms.ModelForm):
    """
    Customer name only.
    Balance is system-calculated and must NOT be edited manually.
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

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()

        if not name:
            raise forms.ValidationError("Customer name cannot be empty.")

        # normalize spacing (prevents duplicates like "Ram  Kumar")
        name = " ".join(name.split())
        return name


# ─────────────────────────────────────
# MILK ENTRY FORM
# ─────────────────────────────────────

class MilkEntryForm(forms.ModelForm):
    """
    Allows:
    - selecting existing customer
    - OR typing a new customer name
    Customer creation happens in the VIEW (single source of truth).
    """

    customer_name = forms.CharField(
        required=False,
        label='New Customer (optional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type new customer name (or leave blank)',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = MilkEntry
        fields = ['customer', 'customer_name', 'date', 'quantity_ml']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'quantity_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1,
                'placeholder': 'Quantity in ml',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # customer optional because customer_name may be used
        self.fields['customer'].required = False
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')

    def clean_quantity_ml(self):
        qty = self.cleaned_data.get('quantity_ml')

        if qty is None:
            raise forms.ValidationError("Quantity is required.")

        if qty < 0:
            raise forms.ValidationError("Quantity cannot be negative.")

        return qty

    def clean(self):
        cleaned = super().clean()

        customer = cleaned.get('customer')
        customer_name = (cleaned.get('customer_name') or '').strip()

        # normalize customer_name spacing
        customer_name = " ".join(customer_name.split())

        if not customer and not customer_name:
            raise forms.ValidationError(
                "Select an existing customer or enter a new customer name."
            )

        cleaned['customer_name'] = customer_name
        return cleaned
