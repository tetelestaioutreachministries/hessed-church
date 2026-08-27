from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("login/", views.HesedLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="core:home"), name="logout"),
]
