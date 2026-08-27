from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from devotionals.models import Devotional
from events.models import Event
from sermons.models import Sermon


class StaticViewSitemap(Sitemap):
    """The site's fixed pages (home, about, list pages, forms)."""

    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:about",
            "events:list",
            "sermons:list",
            "devotionals:list",
            "volunteer:page",
            "groups:page",
            "contactus:page",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "core:home" else 0.6


class EventSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Event.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class SermonSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Sermon.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("sermons:detail", args=[obj.slug])


class DevotionalSitemap(Sitemap):
    changefreq = "never"
    priority = 0.4

    def items(self):
        return Devotional.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("devotionals:detail", args=[obj.pk])
