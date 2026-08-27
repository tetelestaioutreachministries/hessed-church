from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),

    path("devotionals/", views.DevotionalListView.as_view(), name="devotional-list"),
    path("devotionals/new/", views.DevotionalCreateView.as_view(), name="devotional-create"),
    path("devotionals/<int:pk>/edit/", views.DevotionalUpdateView.as_view(), name="devotional-edit"),

    path("sermons/", views.SermonListView.as_view(), name="sermon-list"),
    path("sermons/new/", views.SermonCreateView.as_view(), name="sermon-create"),
    path("sermons/<int:pk>/edit/", views.SermonUpdateView.as_view(), name="sermon-edit"),

    path("events/", views.EventListView.as_view(), name="event-list"),
    path("events/new/", views.EventCreateView.as_view(), name="event-create"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event-edit"),

    path("groups/", views.ConnectGroupListView.as_view(), name="group-list"),
    path("groups/new/", views.ConnectGroupCreateView.as_view(), name="group-create"),
    path("groups/<int:pk>/edit/", views.ConnectGroupUpdateView.as_view(), name="group-edit"),

    path("departments/", views.DepartmentListView.as_view(), name="department-list"),
    path("departments/<int:pk>/edit/", views.DepartmentUpdateView.as_view(), name="department-edit"),

    path("inbox/", views.InboxView.as_view(), name="inbox"),
    path("inbox/<str:kind>/<int:pk>/toggle/", views.mark_handled, name="inbox-toggle"),

    path("subscribers/", views.SubscriberListView.as_view(), name="subscriber-list"),
    path("subscribers/<int:pk>/toggle/", views.toggle_subscriber, name="subscriber-toggle"),
]
