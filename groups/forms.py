from django import forms

from .models import ConnectGroup, GroupInquiry


class GroupInquiryForm(forms.ModelForm):
    class Meta:
        model = GroupInquiry
        fields = ["name", "email", "phone", "facebook", "age", "availability", "group", "comments"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Your Name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Your Email",
            }),
            "phone": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Mobile Number", "type": "tel",
            }),
            "facebook": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Facebook URL",
            }),
            "age": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Your Age",
            }),
            "availability": forms.TextInput(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Availability (Day & Time)",
            }),
            "group": forms.Select(attrs={"class": "h-full-width h-remove-bottom"}),
            "comments": forms.Textarea(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Comments & Questions",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].queryset = ConnectGroup.objects.filter(is_active=True)
        self.fields["group"].required = False
        self.fields["group"].empty_label = "No preference"
        for name in ("phone", "facebook", "age", "availability", "comments"):
            self.fields[name].required = False
