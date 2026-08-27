from django import forms

from .models import Subscriber


class SubscribeForm(forms.Form):
    """Plain (non-ModelForm) so a repeat signup from someone who previously
    unsubscribed doesn't hit a 'unique' validation error — the view handles
    re-activating an existing Subscriber instead."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "h-full-width h-remove-bottom", "placeholder": "Your email address"})
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
