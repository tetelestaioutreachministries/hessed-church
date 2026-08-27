from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import DeviceToken, Profile
from devotionals.models import Devotional
from events.models import Event, EventRSVP
from sermons.models import Sermon

from .serializers import DevotionalSerializer, EventSerializer, SermonSerializer


class DevotionalTodayView(RetrieveAPIView):
    """GET /api/devotionals/today/ — 404 if none published yet.
    Flutter fetches this on launch and caches the result offline with Hive."""

    serializer_class = DevotionalSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        devotional = Devotional.objects.filter(date=timezone.localdate(), is_published=True).first()
        if devotional is None:
            from django.http import Http404
            raise Http404("No devotional published for today yet.")
        return devotional


class SermonViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/sermons/ — paginated list of sermons."""

    queryset = Sermon.objects.filter(is_published=True).select_related("series").all()
    serializer_class = SermonSerializer
    permission_classes = [permissions.AllowAny]


class UpcomingEventViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/events/upcoming/ — paginated list of published, upcoming events."""

    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.filter(is_published=True, date__gte=timezone.localdate())


class GoogleAuthView(APIView):
    """POST /api/auth/google/ — {"id_token": "..."}
    Verifies the Google idToken, creates/logs in the corresponding user +
    Profile, and returns a DRF auth token for subsequent requests."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token_str = request.data.get("id_token")
        if not id_token_str:
            return Response({"detail": "id_token is required."}, status=status.HTTP_400_BAD_REQUEST)

        from django.conf import settings
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token

        try:
            idinfo = google_id_token.verify_oauth2_token(
                id_token_str, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID or None
            )
        except ValueError as exc:
            return Response({"detail": f"Invalid Google token: {exc}"}, status=status.HTTP_401_UNAUTHORIZED)

        google_sub = idinfo["sub"]
        email = idinfo.get("email", "")
        name = idinfo.get("name", "") or email.split("@")[0]

        UserModel = get_user_model()
        profile = Profile.objects.filter(google_sub=google_sub).first()
        if profile:
            user = profile.user
        else:
            user, _ = UserModel.objects.get_or_create(
                username=email or f"google-{google_sub}",
                defaults={"email": email, "first_name": name},
            )
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.google_sub = google_sub
            profile.avatar_url = idinfo.get("picture", "")
            profile.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": {"id": user.id, "email": user.email, "name": user.get_full_name()}})


class EventRSVPView(APIView):
    """POST /api/events/<id>/rsvp/ — auth required, idempotent."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            event = Event.objects.get(pk=pk, is_published=True)
        except Event.DoesNotExist:
            return Response({"detail": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

        rsvp, created = EventRSVP.objects.get_or_create(event=event, user=request.user)
        return Response(
            {"event": event.id, "rsvp_created": created, "rsvp_at": rsvp.created_at},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class DeviceRegisterView(APIView):
    """POST /api/devices/register/ — {"token": "..."}; auth optional so
    anonymous devices can still register for the daily devotional push."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        fcm_token = request.data.get("token")
        if not fcm_token:
            return Response({"detail": "token is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        device, created = DeviceToken.objects.update_or_create(
            token=fcm_token, defaults={"user": user}
        )
        return Response({"registered": True, "created": created})
