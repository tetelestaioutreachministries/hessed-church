from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import SubscribeForm
from .models import Subscriber


def _safe_next(request, fallback="core:home"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    from django.urls import reverse
    return reverse(fallback)


def subscribe(request):
    if request.method != "POST":
        return redirect(_safe_next(request))

    form = SubscribeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=["is_active"])
        messages.success(request, "You're subscribed! We'll email you when a new sermon or event is posted.")
    else:
        messages.error(request, "Please enter a valid email address.")

    return redirect(_safe_next(request))


def unsubscribe(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    if subscriber.is_active:
        subscriber.is_active = False
        subscriber.save(update_fields=["is_active"])
    return render(request, "newsletter/unsubscribed.html", {"email": subscriber.email})
