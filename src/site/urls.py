from django.urls import path

from . import views

app_name = "site"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("services/", views.services_view, name="services"),
    path("contacts/", views.contacts_view, name="contacts"),
]
