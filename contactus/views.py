from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import ContactMessageForm


def contact_page(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            send_mail(
                subject=f"New contact form message from {contact_message.name}",
                message=(
                    f"Name: {contact_message.name}\n"
                    f"Email: {contact_message.email}\n"
                    f"Website: {contact_message.website}\n\n"
                    f"Message:\n{contact_message.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CHURCH_GENERAL_EMAIL],
                fail_silently=True,
            )
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
            return redirect("contactus:page")
    else:
        form = ContactMessageForm()

    return render(request, "contactus/page.html", {"form": form})
