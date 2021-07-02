from django.urls import path

from . import views

app_name = "site"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
]
