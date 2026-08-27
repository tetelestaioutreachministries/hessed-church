from django.urls import path

from . import views

app_name = "volunteer"

urlpatterns = [
    path("", views.volunteer_page, name="page"),
]
