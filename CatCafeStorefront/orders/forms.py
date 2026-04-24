from django import forms
from django.utils import timezone


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    billing_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    card_number = forms.CharField(
        max_length=16,
        min_length=16,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    expiration_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']

        if not card_number.isdigit():
            raise forms.ValidationError("Card number must contain exactly 16 digits.")

        if len(card_number) != 16:
            raise forms.ValidationError("Card number must be exactly 16 digits.")

        return card_number

    def clean_expiration_date(self):
        expiration_date = self.cleaned_data['expiration_date']

        if expiration_date <= timezone.localdate():
            raise forms.ValidationError("Expiration date must be after today's date.")

        return expiration_date

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']

        if not cvv.isdigit():
            raise forms.ValidationError("CVV must contain exactly 3 digits.")

        if len(cvv) != 3:
            raise forms.ValidationError("CVV must be exactly 3 digits.")

        return cvv