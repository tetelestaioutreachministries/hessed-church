from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Syncs the django.contrib.sites domain (used by sitemap.xml) with "
        "SITE_BASE_URL, so the sitemap doesn't show 'example.com'. Safe to "
        "run every deploy — it's a no-op if the domain is already correct."
    )

    def handle(self, *args, **options):
        domain = urlparse(settings.SITE_BASE_URL).netloc or settings.SITE_BASE_URL
        site, created = Site.objects.update_or_create(
            id=settings.SITE_ID,
            defaults={"domain": domain, "name": settings.CHURCH_NAME},
        )
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} site domain -> {domain}"))
