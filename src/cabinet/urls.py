from django.urls import path

from . import views

app_name = "cabinet"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("receipts/", views.receipt_list_view, name="receipt_list"),
    path("receipts/detail/<int:pk>", views.ReceiptDetailView.as_view(), name="receipt_detail"),
]
