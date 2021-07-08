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

    path("flats/", views.FlatListView.as_view(), name="flat_list"),
    path("flats/create/", views.flat_create_view, name="flat_create"),
    path("flats/detail/<int:pk>/", views.FlatDetailView.as_view(), name="flat_detail"),
    path("flats/update/<int:pk>/", views.flat_update_view, name="flat_update"),
    path("flats/delete/<int:pk>/", views.FlatDeleteView.as_view(), name="flat_delete"),

    path("website/home/", views.site_home_view, name="site_home"),
    path("website/about/", views.site_about_view, name="site_about"),
    path("website/services/", views.site_services_view, name="site_services"),
    path("website/contacts/", views.site_contacts_view, name="site_contacts"),
    path("website/update-sitemap/", views.update_sitemap_view, name="update_sitemap"),
    path("website/delete-gallery-image/<int:pk>/", views.GalleryImageDeleteView.as_view(), name="delete_gallery_image"),
    path("website/delete-document/<int:pk>/", views.DocumentDeleteView.as_view(), name="delete_document"),
    path("website/delete-article/<int:pk>/", views.ArticleDeleteView.as_view(), name="delete_article",),

    path("api/sections/<int:pk>/", views.api_sections, name="api_sections"),
    path("api/floors/<int:pk>/", views.api_floors, name="api_floors"),
    path("api/users/", views.api_users, name="api_users"),
    path("api/users/new/", views.api_new_users, name="api_new_users"),

    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/create/", views.user_create_view, name="user_create"),
    path("users/detail/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("users/update/<int:pk>/", views.user_update_view, name="user_update"),
    path("users/delete/<int:pk>/", views.UserDeleteView.as_view(), name="user_delete"),

    path("system/services/", views.system_services, name="system_services"),
    path("system/services/delete/measure/<int:pk>/", views.MeasureDeleteView.as_view(), name="delete_measure"),
    path("system/services/delete/service/<int:pk>/", views.ServiceDeleteView.as_view(), name="delete_service"),
    path("system/services/check/measure/<int:pk>/", views.check_measure, name="check_measure"),
    path("system/services/check/service/<int:pk>/", views.check_service, name="check_service"),
]
