import os

from allauth.utils import build_absolute_uri
from birthday.fields import BirthdayField
from birthday.managers import BirthdayManager
from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from src.admin_panel.services.media_services import UploadToPathAndRename
from src.admin_panel.services.user_passes_test import check_access


class UserRole(models.Model):
    name = models.CharField(max_length=255, unique=True)

    statistics_access = models.BooleanField(default=0)
    cashbox_access = models.BooleanField(default=0)
    receipt_access = models.BooleanField(default=0)
    account_access = models.BooleanField(default=0)
    flat_access = models.BooleanField(default=0)
    house_user_access = models.BooleanField(default=0)
    house_access = models.BooleanField(default=0)
    message_access = models.BooleanField(default=0)
    call_request_access = models.BooleanField(default=0)
    meter_data_access = models.BooleanField(default=0)
    site_access = models.BooleanField(default=0)
    service_access = models.BooleanField(default=0)
    tariff_access = models.BooleanField(default=0)
    role_access = models.BooleanField(default=0)
    staff_access = models.BooleanField(default=0)
    payments_detail_access = models.BooleanField(default=0)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = models.CharField(_("username"), max_length=150)
    upload_path = os.path.join(MEDIA_ROOT, "images", "site", "home_page", "articles")

    class UserStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("Активный")
        INACTIVE = "NEW", _("Новый")
        DEACTIVATED = "DEACTIVATED", _("Отключен")

    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    patronymic = models.CharField(_("patronymic"), max_length=150)
    description = models.CharField(max_length=3000, null=True, blank=True)
    birthday = BirthdayField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    phone = PhoneNumberField(null=True, blank=True)
    viber = PhoneNumberField(null=True, blank=True)
    telegram = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=150)
    status = models.CharField(max_length=11, choices=UserStatus.choices)
    user_id = models.CharField(max_length=20, null=True, blank=True)
    role = models.ForeignKey(UserRole, null=True, blank=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    def serialize(self, pattern):
        if pattern == "select2":
            data = {"id": self.id, "text": self.full_name}
            return data
        if pattern == "select2-staff":
            data = {"id": self.id, "text": f'{self.full_name} - {self.role.name}'}
            return data
        if pattern == "api_new_users":
            data = {"id": self.id, "full_name": self.full_name}
            return data

    def __str__(self):
        return self.full_name
