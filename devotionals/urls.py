from django.urls import path

from . import views

app_name = "devotionals"

urlpatterns = [
    path("", views.devotional_list, name="list"),
    path("<int:pk>/", views.devotional_detail, name="detail"),
    path("trigger-push/", views.trigger_devotional_push, name="trigger-push"),
]
