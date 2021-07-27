from django.urls import path

from . import views

app_name = "cabinet"
urlpatterns = [
    path("", views.home_view, name="home"),

    path("receipts/", views.receipt_list_view, name="receipt_list"),
    path("receipts/detail/<int:pk>/", views.ReceiptDetailView.as_view(), name="receipt_detail"),
    path("receipts/print/<int:pk>/", views.receipt_print_view, name="receipt_print"),
    path("receipts/pdf/<int:pk>/", views.receipt_pdf_view, name="receipt_pdf"),

    path("tariffs/", views.tariff_list_view, name="tariff_list"),

    path("messages/", views.MessageListView.as_view(), name="message_list"),

    path("call-requests/", views.CallRequestListView.as_view(), name="call_request_list"),

    path("profile/", views.user_profile_detail_view, name="user_profile_detail"),
    path("profile/update/", views.user_profile_update_view, name="user_profile_update"),
]
