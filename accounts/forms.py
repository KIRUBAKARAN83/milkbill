class MilkEntryForm(forms.ModelForm):
    customer_name = forms.CharField(
        required=False,
        label="New Customer (optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new customer name'
        })
    )

    class Meta:
        model = MilkEntry
        fields = ['customer', 'customer_name', 'date', 'quantity_ml']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': False   # 🔥 CRITICAL
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'quantity_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Quantity in ml'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🔥 REMOVE HTML required flag
        self.fields['customer'].required = False

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        customer_name = cleaned_data.get('customer_name')

        if customer_name:
            cleaned_data['customer_name'] = customer_name.strip()

        if not customer and not customer_name:
            raise forms.ValidationError(
                "Select an existing customer OR enter a new customer name."
            )

        if customer and customer_name:
            raise forms.ValidationError(
                "Please choose only one: existing customer OR new customer."
            )

        return cleaned_data
