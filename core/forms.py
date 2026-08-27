from django.contrib.auth.forms import AuthenticationForm
from django import forms


class HesedAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = forms.TextInput(attrs={
            "class": "h-full-width h-remove-bottom", "placeholder": "Username", "autofocus": True,
        })
        self.fields["password"].widget = forms.PasswordInput(attrs={
            "class": "h-full-width h-remove-bottom", "placeholder": "Password",
        })
