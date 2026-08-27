from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import redirect, render

from .forms import VolunteerApplicationForm
from .models import Department


def volunteer_page(request):
    if request.method == "POST":
        form = VolunteerApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()

            # Notify the department contact (falls back to the general church
            # email if the department has none set), reply-to the applicant.
            email = EmailMessage(
                subject=f"New volunteer application: {application.department.name}",
                body=(
                    f"Name: {application.name}\n"
                    f"Email: {application.email}\n"
                    f"Phone: {application.phone}\n"
                    f"Facebook: {application.facebook}\n"
                    f"First time to serve: {'Yes' if application.is_first_time else 'No'}\n\n"
                    f"Comments:\n{application.comments}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[application.department.recipient_email],
                reply_to=[application.email],
            )
            email.send(fail_silently=True)

            # Confirmation email to the applicant.
            send_mail(
                subject=f"Thanks for volunteering with {settings.CHURCH_NAME}!",
                message=(
                    f"Hi {application.name},\n\n"
                    f"Thank you for your interest in serving with the {application.department.name} "
                    f"team at {settings.CHURCH_NAME}. Someone from the team will be in touch soon.\n\n"
                    f"God bless,\n{settings.CHURCH_NAME}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.email],
                fail_silently=True,
            )

            messages.success(request, "Thank you for volunteering! We've sent a confirmation to your email.")
            return redirect("volunteer:page")
    else:
        form = VolunteerApplicationForm()

    departments = Department.objects.filter(is_active=True)
    return render(request, "volunteer/page.html", {"form": form, "departments": departments})
