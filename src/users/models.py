import os

from birthday.fields import BirthdayField
from birthday.managers import BirthdayManager
from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from src.admin_panel.services.media_services import UploadToPathAndRename


class User(AbstractUser):
    username = models.CharField(_('username'), max_length=150)
    upload_path = os.path.join(MEDIA_ROOT, "images", "site", "home_page", "articles")

    class UserStatus(models.TextChoices):
        ACTIVE = "ACTIVE", _("Активный")
        INACTIVE = "INACTIVE", _("Неактивный")
        DEACTIVATED = "DEACTIVATED", _("Деактивированный")

    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    patronymic = models.CharField(_("patronymic"), max_length=150)
    description = models.CharField(max_length=3000, null=True, blank=True)
    birthday = BirthdayField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    phone = PhoneNumberField()
    viber = PhoneNumberField(null=True, blank=True)
    telegram = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=150)
    status = models.CharField(max_length=11, choices=UserStatus.choices)
    user_id = models.CharField(max_length=20, unique=True)

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
            text = self.full_name
            return {"id": self.id, "text": text}

    def __str__(self):
        return self.full_name
