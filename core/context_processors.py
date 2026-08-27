from django.conf import settings
from django.templatetags.static import static

_APP_TO_NAV = {
    "core": None,  # resolved below by url_name (home vs about)
    "events": "events",
    "sermons": "sermons",
    "devotionals": "devotionals",
    "volunteer": "volunteer",
    "groups": "groups",
    "contactus": "contact",
    "dashboard": "manage",
}


def church_info(request):
    """Makes church-wide info (and the active nav item) available in every template."""
    active_nav = None
    match = getattr(request, "resolver_match", None)
    if match:
        if match.app_name == "core":
            active_nav = "about" if match.url_name == "about" else "home"
        else:
            active_nav = _APP_TO_NAV.get(match.app_name)

    default_og_image = request.build_absolute_uri(static("images/hero-bg-3000.jpg"))

    return {
        "CHURCH_NAME": settings.CHURCH_NAME,
        "CHURCH_ADDRESS": settings.CHURCH_ADDRESS,
        "CHURCH_PHONE": settings.CHURCH_PHONE,
        "CHURCH_GENERAL_EMAIL": settings.CHURCH_GENERAL_EMAIL,
        "active_nav": active_nav,
        "GOOGLE_SITE_VERIFICATION": settings.GOOGLE_SITE_VERIFICATION,
        "DEFAULT_OG_IMAGE": default_og_image,
        "CANONICAL_URL": request.build_absolute_uri(request.path),
        "SITE_BASE_URL": settings.SITE_BASE_URL,
    }
