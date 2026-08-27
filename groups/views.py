from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render

from .forms import GroupInquiryForm
from .models import ConnectGroup


def group_page(request):
    if request.method == "POST":
        form = GroupInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            send_mail(
                subject=f"New Connect Group inquiry from {inquiry.name}",
                message=(
                    f"Name: {inquiry.name}\n"
                    f"Email: {inquiry.email}\n"
                    f"Phone: {inquiry.phone}\n"
                    f"Facebook: {inquiry.facebook}\n"
                    f"Age: {inquiry.age}\n"
                    f"Availability: {inquiry.availability}\n"
                    f"Group requested: {inquiry.group or 'No preference'}\n\n"
                    f"Comments:\n{inquiry.comments}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.recipient_email],
                fail_silently=True,
            )
            messages.success(request, "Thanks! We've received your request and someone will reach out soon.")
            return redirect("groups:page")
    else:
        form = GroupInquiryForm()

    groups = ConnectGroup.objects.filter(is_active=True)
    return render(request, "groups/page.html", {"form": form, "groups": groups})
