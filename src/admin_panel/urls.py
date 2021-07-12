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
    path("api/measure/", views.api_measure_name, name="api_measure_name"),

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

    path("system/tariffs/", views.SystemTariffsListView.as_view(), name="system_tariffs"),
    path("system/tariffs/create/", views.system_tariffs_create_view, name="system_tariffs_create"),
    path("system/tariffs/update/<int:pk>/", views.system_tariffs_update_view, name="system_tariffs_update"),
    path("system/tariffs/delete/<int:pk>/", views.TariffDeleteView.as_view(), name="system_tariffs_delete"),
    path("system/tariffs/clone/<int:pk>/", views.system_tariffs_clone_view, name="system_tariffs_clone"),
    path("system/tariffs/detail/<int:pk>/", views.TariffDetailView.as_view(), name="system_tariffs_detail"),

    path("system/staff/", views.StaffListView.as_view(), name="system_staff_list"),
    path("system/staff/roles", views.system_user_role_view, name="system_staff_roles"),
    path("system/staff/create/", views.staff_create_view, name="system_staff_create"),
    path("system/staff/update/<int:pk>/", views.staff_update_view, name="system_staff_update"),
    path("system/staff/delete/<int:pk>/", views.StaffDeleteView.as_view(), name="system_staff_delete"),
    path("system/staff/detail/<int:pk>/", views.StaffDetailView.as_view(), name="system_staff_detail"),

    path("system/credentials/", views.credentials_update_view, name="system_credentials"),
]
