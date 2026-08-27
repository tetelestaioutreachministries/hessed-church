from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Series, Sermon


def sermon_list(request):
    sermons = Sermon.objects.filter(is_published=True).select_related("series").order_by("-date")

    series_id = request.GET.get("series")
    if series_id:
        sermons = sermons.filter(series_id=series_id)

    paginator = Paginator(sermons, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    all_series = Series.objects.filter(sermons__is_published=True).distinct().order_by("-created_at")

    return render(request, "sermons/list.html", {
        "page_obj": page_obj,
        "sermons": page_obj.object_list,
        "all_series": all_series,
        "selected_series_id": int(series_id) if series_id else None,
    })


def sermon_detail(request, slug):
    sermon = get_object_or_404(Sermon.objects.select_related("series"), slug=slug, is_published=True)
    return render(request, "sermons/detail.html", {"sermon": sermon})
