from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("sermons", views.SermonViewSet, basename="sermon")
router.register("events/upcoming", views.UpcomingEventViewSet, basename="event-upcoming")

urlpatterns = [
    path("devotionals/today/", views.DevotionalTodayView.as_view(), name="devotional-today"),
    path("auth/google/", views.GoogleAuthView.as_view(), name="auth-google"),
    path("events/<int:pk>/rsvp/", views.EventRSVPView.as_view(), name="event-rsvp"),
    path("devices/register/", views.DeviceRegisterView.as_view(), name="device-register"),
    path("", include(router.urls)),
]
