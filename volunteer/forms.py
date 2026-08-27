from django import forms

from .models import Department, VolunteerApplication

FIRST_TIME_CHOICES = (
    (True, "Yes"),
    (False, "No"),
)


class VolunteerApplicationForm(forms.ModelForm):
    is_first_time = forms.TypedChoiceField(
        label="This is my first time to serve",
        choices=FIRST_TIME_CHOICES,
        coerce=lambda v: v == "True",
        widget=forms.Select(attrs={"class": "h-full-width h-remove-bottom"}),
    )

    class Meta:
        model = VolunteerApplication
        fields = ["name", "email", "phone", "facebook", "department", "is_first_time", "comments"]
        labels = {"department": "Ministry to volunteer"}
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
            "department": forms.Select(attrs={"class": "h-full-width h-remove-bottom"}),
            "comments": forms.Textarea(attrs={
                "class": "h-full-width h-remove-bottom", "placeholder": "Comments & Questions",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["department"].queryset = Department.objects.filter(is_active=True)
        for name in ("phone", "facebook", "comments"):
            self.fields[name].required = False
