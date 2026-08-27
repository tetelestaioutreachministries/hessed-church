from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from contactus.models import ContactMessage
from core.media_processing import compress_audio_to_64kbps, compress_image_under_300kb, upload_to_cloudinary
from core.push import send_push_to_all_devices
from devotionals.models import Devotional
from events.models import Event
from groups.models import ConnectGroup, GroupInquiry
from newsletter.models import Subscriber
from newsletter.services import notify_new_event, notify_new_sermon
from sermons.models import Sermon
from volunteer.models import Department, VolunteerApplication

from .forms import (
    ConnectGroupManageForm,
    DepartmentManageForm,
    DevotionalForm,
    EventManageForm,
    SermonManageForm,
)
from .mixins import StaffRequiredMixin


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["counts"] = {
            "devotionals": Devotional.objects.count(),
            "sermons": Sermon.objects.count(),
            "events": Event.objects.count(),
            "groups": ConnectGroup.objects.count(),
            "departments": Department.objects.count(),
            "unhandled_inbox": (
                ContactMessage.objects.filter(is_handled=False).count()
                + VolunteerApplication.objects.filter(is_handled=False).count()
                + GroupInquiry.objects.filter(is_handled=False).count()
            ),
            "subscribers": Subscriber.objects.filter(is_active=True).count(),
        }
        return ctx


# ---------------------------------------------------------------------------
# Devotionals
# ---------------------------------------------------------------------------

class DevotionalListView(StaffRequiredMixin, ListView):
    model = Devotional
    template_name = "dashboard/devotional_list.html"
    context_object_name = "devotionals"
    paginate_by = 20


class DevotionalCreateView(StaffRequiredMixin, CreateView):
    model = Devotional
    form_class = DevotionalForm
    template_name = "dashboard/devotional_form.html"
    success_url = reverse_lazy("dashboard:devotional-list")

    def form_valid(self, form):
        messages.success(self.request, "Devotional saved. It'll go out in tomorrow's 6 AM push if dated today or later.")
        return super().form_valid(form)


class DevotionalUpdateView(StaffRequiredMixin, UpdateView):
    model = Devotional
    form_class = DevotionalForm
    template_name = "dashboard/devotional_form.html"
    success_url = reverse_lazy("dashboard:devotional-list")

    def form_valid(self, form):
        messages.success(self.request, "Devotional updated.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Sermons
# ---------------------------------------------------------------------------

class SermonListView(StaffRequiredMixin, ListView):
    model = Sermon
    template_name = "dashboard/sermon_list.html"
    context_object_name = "sermons"
    paginate_by = 20
    queryset = Sermon.objects.select_related("series")


def _handle_sermon_audio_upload(request, sermon, audio_file):
    if not audio_file:
        return
    try:
        compressed_path, size_mb = compress_audio_to_64kbps(audio_file)
        result = upload_to_cloudinary(compressed_path, folder="sermons")
    except Exception as exc:
        messages.error(
            request,
            "The sermon was saved, but the audio upload failed — check that Cloudinary is configured "
            f"(CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET). Details: {exc}",
        )
        return
    sermon.audio_url = result["secure_url"]
    sermon.cloudinary_id = result["public_id"]
    sermon.file_size_mb = size_mb
    sermon.save()
    messages.success(request, f"Audio uploaded to Cloudinary ({size_mb} MB).")


class SermonCreateView(StaffRequiredMixin, CreateView):
    model = Sermon
    form_class = SermonManageForm
    template_name = "dashboard/sermon_form.html"
    success_url = reverse_lazy("dashboard:sermon-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        audio_file = form.cleaned_data.get("audio_file")
        _handle_sermon_audio_upload(self.request, self.object, audio_file)

        has_content = bool(self.object.audio_url) or bool(self.object.video_url)
        if has_content and self.object.is_published:
            notify_new_sermon(self.object, request=self.request)
            if audio_file:
                send_push_to_all_devices(
                    title="New Sermon",
                    body=f"{self.object.title} is now available",
                    data={"type": "sermon", "sermon_id": str(self.object.pk)},
                )
        elif not audio_file:
            messages.success(self.request, "Sermon saved (no audio uploaded yet — you can add it later).")
        return response


class SermonUpdateView(StaffRequiredMixin, UpdateView):
    model = Sermon
    form_class = SermonManageForm
    template_name = "dashboard/sermon_form.html"
    success_url = reverse_lazy("dashboard:sermon-list")

    def form_valid(self, form):
        # form.is_valid() (already run by this point) mutates self.object's
        # in-memory fields via construct_instance — so self.object already
        # reflects the *new* values here, not what's in the DB. Query the DB
        # separately to get the true pre-edit state.
        original = Sermon.objects.filter(pk=self.object.pk).first()
        had_content = bool(original.audio_url) or bool(original.video_url) if original else False

        response = super().form_valid(form)
        audio_file = form.cleaned_data.get("audio_file")
        _handle_sermon_audio_upload(self.request, self.object, audio_file)

        has_content_now = bool(self.object.audio_url) or bool(self.object.video_url)
        if not had_content and has_content_now and self.object.is_published:
            # First time this sermon has audio or video attached — this is
            # the "new full sermon" moment subscribers signed up for.
            notify_new_sermon(self.object, request=self.request)
            if audio_file:
                send_push_to_all_devices(
                    title="New Sermon",
                    body=f"{self.object.title} is now available",
                    data={"type": "sermon", "sermon_id": str(self.object.pk)},
                )
        elif not audio_file:
            messages.success(self.request, "Sermon updated.")
        return response


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class EventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = "dashboard/event_list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        return Event.objects.order_by("-date")


def _handle_event_poster_upload(request, event, poster_file):
    if not poster_file:
        return
    try:
        compressed_path = compress_image_under_300kb(poster_file)
        result = upload_to_cloudinary(compressed_path, folder="posters")
    except Exception as exc:
        messages.error(
            request,
            "The event was saved, but the poster upload failed — check that Cloudinary is configured "
            f"(CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET). Details: {exc}",
        )
        return
    event.poster_url = result["secure_url"]
    event.cloudinary_id = result["public_id"]
    event.save()
    messages.success(request, "Poster uploaded to Cloudinary.")


class EventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    form_class = EventManageForm
    template_name = "dashboard/event_form.html"
    success_url = reverse_lazy("dashboard:event-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        poster_file = form.cleaned_data.get("poster_file")
        _handle_event_poster_upload(self.request, self.object, poster_file)
        if self.object.is_published:
            notify_new_event(self.object, request=self.request)
        if not poster_file:
            messages.success(self.request, "Event saved.")
        return response


class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventManageForm
    template_name = "dashboard/event_form.html"
    success_url = reverse_lazy("dashboard:event-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        poster_file = form.cleaned_data.get("poster_file")
        _handle_event_poster_upload(self.request, self.object, poster_file)
        if not poster_file:
            messages.success(self.request, "Event updated.")
        return response


# ---------------------------------------------------------------------------
# Connect Groups & Volunteer Departments
# ---------------------------------------------------------------------------

class ConnectGroupListView(StaffRequiredMixin, ListView):
    model = ConnectGroup
    template_name = "dashboard/group_list.html"
    context_object_name = "groups"


class ConnectGroupCreateView(StaffRequiredMixin, CreateView):
    model = ConnectGroup
    form_class = ConnectGroupManageForm
    template_name = "dashboard/group_form.html"
    success_url = reverse_lazy("dashboard:group-list")


class ConnectGroupUpdateView(StaffRequiredMixin, UpdateView):
    model = ConnectGroup
    form_class = ConnectGroupManageForm
    template_name = "dashboard/group_form.html"
    success_url = reverse_lazy("dashboard:group-list")


class DepartmentListView(StaffRequiredMixin, ListView):
    model = Department
    template_name = "dashboard/department_list.html"
    context_object_name = "departments"


class DepartmentUpdateView(StaffRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentManageForm
    template_name = "dashboard/department_form.html"
    success_url = reverse_lazy("dashboard:department-list")


# ---------------------------------------------------------------------------
# Inbox: contact messages, volunteer applications, group inquiries
# ---------------------------------------------------------------------------

class InboxView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/inbox.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["contact_messages"] = ContactMessage.objects.all()[:50]
        ctx["volunteer_applications"] = VolunteerApplication.objects.select_related("department").all()[:50]
        ctx["group_inquiries"] = GroupInquiry.objects.select_related("group").all()[:50]
        return ctx


def mark_handled(request, kind, pk):
    """Toggles is_handled for a contact message / volunteer application /
    group inquiry, then redirects back to the inbox."""
    if not request.user.is_staff:
        return redirect("dashboard:home")

    model_map = {
        "contact": ContactMessage,
        "volunteer": VolunteerApplication,
        "group": GroupInquiry,
    }
    model = model_map.get(kind)
    if model is None:
        messages.error(request, "Unknown inbox item type.")
        return redirect("dashboard:inbox")

    obj = get_object_or_404(model, pk=pk)
    obj.is_handled = not obj.is_handled
    obj.save(update_fields=["is_handled"])
    return redirect("dashboard:inbox")


# ---------------------------------------------------------------------------
# Newsletter subscribers
# ---------------------------------------------------------------------------

class SubscriberListView(StaffRequiredMixin, ListView):
    model = Subscriber
    template_name = "dashboard/subscriber_list.html"
    context_object_name = "subscribers"
    paginate_by = 50


def toggle_subscriber(request, pk):
    if not request.user.is_staff:
        return redirect("dashboard:home")
    subscriber = get_object_or_404(Subscriber, pk=pk)
    subscriber.is_active = not subscriber.is_active
    subscriber.save(update_fields=["is_active"])
    return redirect("dashboard:subscriber-list")
