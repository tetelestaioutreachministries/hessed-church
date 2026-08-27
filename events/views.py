from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Event


def event_list(request):
    upcoming = Event.objects.filter(is_published=True, date__gte=timezone.localdate())
    paginator = Paginator(upcoming, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "events/list.html", {"page_obj": page_obj, "events": page_obj.object_list})


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    return render(request, "events/detail.html", {"event": event})
