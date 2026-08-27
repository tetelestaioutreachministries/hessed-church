from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "website", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Your Name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Your Email",
            }),
            "website": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Website",
            }),
            "message": forms.Textarea(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Your Message",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["website"].required = False
