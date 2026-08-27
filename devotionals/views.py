from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Devotional
from .services import send_todays_devotional_push


def devotional_list(request):
    devotionals = Devotional.objects.filter(
        is_published=True, date__lte=timezone.localdate()
    ).order_by("-date")
    paginator = Paginator(devotionals, 7)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "devotionals/list.html", {"page_obj": page_obj, "devotionals": page_obj.object_list})


def devotional_detail(request, pk):
    devotional = get_object_or_404(
        Devotional, pk=pk, is_published=True, date__lte=timezone.localdate()
    )
    return render(request, "devotionals/detail.html", {"devotional": devotional})


def trigger_devotional_push(request):
    """External-scheduler-friendly endpoint (e.g. cron-job.org) that runs
    the same daily devotional push as `manage.py send_devotional_push`,
    for hosting setups without a paid host-level Cron Job. Protected by a
    shared secret token in the query string so random internet traffic
    can't trigger it. GET-only: no state changes to a *record*, it just
    sends a push, so CSRF protection (which only applies to unsafe methods
    changing server-side data on behalf of a browser session) isn't the
    relevant defense here — the secret token is.
    """
    token = request.GET.get("token", "")
    if not settings.CRON_SECRET_TOKEN or token != settings.CRON_SECRET_TOKEN:
        return HttpResponseForbidden("Invalid or missing token.")

    result = send_todays_devotional_push()
    return HttpResponse(result, content_type="text/plain")
