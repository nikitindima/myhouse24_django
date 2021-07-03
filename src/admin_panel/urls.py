from django.urls import path

from . import views

app_name = "admin_panel"
urlpatterns = [
    path("", views.home_view, name="home"),

    path("houses/", views.HouseListView.as_view(), name="house_list"),
    path("houses/create/", views.house_create_view, name="house_create"),
    path("houses/detail/<int:pk>/", views.HouseDetailView.as_view(), name="house_detail"),
    path("houses/update/<int:pk>/", views.house_update_view, name="house_update"),
    path("houses/delete/<int:pk>/", views.HouseDeleteView.as_view(), name="house_delete"),

    path("section/delete/", views.section_delete_view, name="section_delete"),

    path("website/home/", views.site_home_view, name="site_home"),
    path("website/about/", views.site_about_view, name="site_about"),
    path("website/services/", views.site_services_view, name="site_services"),
    path("website/contacts/", views.site_contacts_view, name="site_contacts"),
    path("website/update-sitemap/", views.update_sitemap_view, name="update_sitemap"),
    path("website/delete-gallery-image/<int:pk>/", views.GalleryImageDeleteView.as_view(), name="delete_gallery_image"),
    path("website/delete-document/<int:pk>/", views.DocumentDeleteView.as_view(), name="delete_document"),
    path("website/delete-article/<int:pk>/", views.ArticleDeleteView.as_view(), name="delete_article"),
]
