"""
Django settings for hesed_church project (Phase 1: website backend).
"""

from pathlib import Path

import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Core / security
# --------------------------------------------------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-insecure-secret-key-change-me")
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# For platforms like Render/Railway that put the app behind a load balancer
# terminating HTTPS, this tells Django to trust the X-Forwarded-Proto header
# instead of seeing every request as plain HTTP.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Full origins (with scheme) allowed to POST forms — needed in production
# because Django's CSRF check compares against these explicitly once the
# site is served over HTTPS on a real domain. e.g.
# "https://www.hesedchurch.org,https://hesedchurch.onrender.com"
CSRF_TRUSTED_ORIGINS = config("DJANGO_CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    # Starts conservative (1 hour) rather than Django's commonly-recommended
    # year-long value — safe to raise once you've confirmed HTTPS is solid
    # in production. See Django's HSTS docs before increasing this.
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# --------------------------------------------------------------------------
# Applications
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Phase 1 apps
    "core",
    "events",
    "sermons",
    "groups",
    "volunteer",
    "contactus",
    "newsletter",

    # Phase 2 apps
    "devotionals",
    "api",
    "dashboard",

    # Third-party (Phase 2)
    "rest_framework",
    "rest_framework.authtoken",
    # "django_celery_beat",  # only needed if you install Celery — see README-phase2.md
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "allauth",
    "allauth.account",
    "dj_rest_auth",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "hesed_church.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Church-wide info (name, address, phone) available in every template.
                "core.context_processors.church_info",
            ],
        },
    },
]

WSGI_APPLICATION = "hesed_church.wsgi.application"

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
# Uses PostgreSQL from the start (Phase 2 adds Celery/production concerns).
# Reads DATABASE_URL from the environment; falls back to a local Postgres
# connection so `manage.py runserver` works out of the box in dev.
DATABASES = {
    "default": dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default="postgres://hesed:hesed@localhost:5432/hesed_church",
        ),
        conn_max_age=600,
    )
}

# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = config("DJANGO_TIME_ZONE", default="Africa/Kampala")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Static & media files
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Email
# --------------------------------------------------------------------------
# Defaults to the console backend for local dev. Set DJANGO_EMAIL_BACKEND
# (and the SMTP variables below) via environment variables in production —
# no code changes needed to switch.
EMAIL_BACKEND = config(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("DJANGO_EMAIL_HOST", default="")
EMAIL_PORT = config("DJANGO_EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("DJANGO_EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("DJANGO_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("DJANGO_EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DJANGO_DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER or "no-reply@hesedchurch.org")

# --------------------------------------------------------------------------
# Church info (exposed to every template via core.context_processors.church_info)
# --------------------------------------------------------------------------
CHURCH_NAME = config("CHURCH_NAME", default="Hesed Church")
CHURCH_ADDRESS = config("CHURCH_ADDRESS", default="1600 Amphitheatre Parkway, Mountain View, CA 94043")
CHURCH_PHONE = config("CHURCH_PHONE", default="+1 975 432 345")
CHURCH_GENERAL_EMAIL = config("CHURCH_GENERAL_EMAIL", default="info@hesedchurch.org")

# Used to build absolute links in newsletter emails when no request is
# available (e.g. sent from /admin/ or a cron job). Set this to your real
# domain in production, e.g. "https://www.hesedchurch.org".
SITE_BASE_URL = config("SITE_BASE_URL", default="http://localhost:8000")

# Google Search Console site-verification meta tag (optional). Paste the
# "content" value Google gives you when verifying via the HTML tag method —
# leave blank to omit the tag entirely.
GOOGLE_SITE_VERIFICATION = config("GOOGLE_SITE_VERIFICATION", default="")

# Shared secret for the free-tier cron alternative (see README-deploy.md).
# An external scheduler (e.g. cron-job.org) calls
# /devotionals/trigger-push/?token=<this value> once a day instead of using
# a paid host-level Cron Job. Leave unset to disable the endpoint entirely
# (it always returns 403 if this is blank).
CRON_SECRET_TOKEN = config("CRON_SECRET_TOKEN", default="")

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/manage/"
LOGOUT_REDIRECT_URL = "/"

# --------------------------------------------------------------------------
# Phase 2 — REST API, Auth, Celery, Cloudinary, Firebase
# --------------------------------------------------------------------------

# --- Django REST Framework -------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Google Sign-In: Flutter sends the idToken, Django verifies it directly with
# the google-auth library against this client ID (see api/views.py).
GOOGLE_OAUTH_CLIENT_ID = config("GOOGLE_OAUTH_CLIENT_ID", default="")

REST_AUTH = {
    "USE_JWT": False,  # plain DRF TokenAuthentication is enough for this app's needs
}

# --- Celery (optional) -------------------------------------------------
# Not required for this project's current scale — the daily devotional push
# runs via cron + `manage.py send_devotional_push` instead (see
# devotionals/services.py). These settings only matter if you install
# celery/redis and choose to use hesed_church/celery.py for other
# background work later.
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_TIMEZONE = "Africa/Kampala"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"  # requires django_celery_beat installed + enabled above
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# --- Cloudinary ---------------------------------------------------------
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")

if CLOUDINARY_CLOUD_NAME:
    # Also used by django-cloudinary-storage for the plain ImageField
    # uploads (Event.image, Series.image) that go through Django's normal
    # storage API — the sermon/poster uploads in core/media_processing.py
    # already call the Cloudinary SDK directly and are unaffected by this.
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
    }
    INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]

# --------------------------------------------------------------------------
# Static & media file storage backends
# --------------------------------------------------------------------------
# Static files: served directly by the app via whitenoise (no separate
# nginx/CDN needed for a site this size).
#
# Media files (uploaded ImageFields like Event.image/Series.image): most
# hosting platforms (Render, Railway, Heroku, etc.) wipe local disk on every
# deploy, so anything saved to MEDIA_ROOT would vanish. If Cloudinary is
# configured, uploaded images go there instead and persist normally; if not
# (e.g. plain local dev), they fall back to the local filesystem as before.
STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if CLOUDINARY_CLOUD_NAME
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Firebase Cloud Messaging ---------------------------------------------
# Path to the Firebase service account JSON. Keep this file out of version
# control; only its path lives in the environment.
FIREBASE_SERVICE_ACCOUNT_JSON = config("FIREBASE_SERVICE_ACCOUNT_JSON", default="")

