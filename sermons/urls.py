from django.urls import path

from . import views

app_name = "sermons"

urlpatterns = [
    path("", views.sermon_list, name="list"),
    path("<slug:slug>/", views.sermon_detail, name="detail"),
]
