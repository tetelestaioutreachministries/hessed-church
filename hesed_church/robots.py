from django.http import HttpResponse


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /manage/",
        "Disallow: /admin/",
        "Disallow: /login/",
        "Disallow: /newsletter/",
        "Disallow: /devotionals/trigger-push/",
        "Disallow: /api/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
