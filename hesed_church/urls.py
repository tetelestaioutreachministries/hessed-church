from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from .robots import robots_txt
from .sitemaps import DevotionalSitemap, EventSitemap, SermonSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "events": EventSitemap,
    "sermons": SermonSitemap,
    "devotionals": DevotionalSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots-txt"),
    path("", include("core.urls")),
    path("events/", include("events.urls")),
    path("sermons/", include("sermons.urls")),
    path("devotionals/", include("devotionals.urls")),
    path("volunteer/", include("volunteer.urls")),
    path("connect-groups/", include("groups.urls")),
    path("contact/", include("contactus.urls")),
    path("newsletter/", include("newsletter.urls")),
    path("api/", include("api.urls")),
    path("manage/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
