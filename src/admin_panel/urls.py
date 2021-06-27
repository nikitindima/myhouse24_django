from django.urls import path

from . import views

app_name = "admin_panel"
urlpatterns = [
    path("", views.home_view, name="home"),

    path("website/home/", views.site_home_view, name="site_home"),
    path("website/about/", views.site_about_view, name="site_about"),
    path("website/services/", views.site_services_view, name="site_services"),
    path("website/contacts/", views.site_contacts_view, name="site_contacts"),
    path("website/update-sitemap/", views.update_sitemap_view, name="update_sitemap")
]
