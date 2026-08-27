from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.utils import timezone

from events.models import Event
from sermons.models import Series

from .forms import HesedAuthenticationForm


class HesedLoginView(LoginView):
    """Branded login page for church staff (replaces /admin/login/ for
    everyday use). Anyone with an account can sign in here; access to
    /manage/ itself is still gated to is_staff by dashboard.mixins."""

    template_name = "core/login.html"
    redirect_authenticated_user = True
    authentication_form = HesedAuthenticationForm


def home(request):
    upcoming_events = Event.objects.filter(
        is_published=True, date__gte=timezone.localdate()
    )[:4]
    current_series = Series.get_current()
    return render(
        request,
        "core/home.html",
        {"upcoming_events": upcoming_events, "current_series": current_series},
    )


def about(request):
    return render(request, "core/about.html")
