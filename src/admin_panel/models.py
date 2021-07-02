import os

from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import ManyToManyField, URLField
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

from .services.media_services import UploadToPathAndRename

User = get_user_model()


# region SITE_CONTROL

# region staff


class Article(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "site", "home_page", "articles")

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    image = models.ImageField(upload_to=UploadToPathAndRename(upload_path))


class SeoData(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    keywords = models.CharField(max_length=2000, null=True, blank=True)


class GalleryImage(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "gallery-images")

    image = models.ImageField(upload_to=UploadToPathAndRename(upload_path))


class Document(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "docs")

    name = models.CharField(max_length=100, blank=False, null=False)
    file = models.FileField(
        upload_to=UploadToPathAndRename(upload_path), blank=False, null=False
    )


# endregion staff
# region pages
class SiteHomePage(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "site", "home_page", "slider")

    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    show_links = models.BooleanField(default=False)
    slider1 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    slider2 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    slider3 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )

    seo_data = models.ForeignKey(SeoData, on_delete=models.CASCADE)
    around_us = models.ManyToManyField(Article)


class SiteAboutPage(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "portraits")

    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    title2 = models.CharField(max_length=100, null=True, blank=True)
    description2 = models.CharField(max_length=3000, null=True, blank=True)
    portrait = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )

    gallery = ManyToManyField(GalleryImage, related_name="gallery")
    gallery2 = ManyToManyField(GalleryImage, related_name="gallery2")

    docs = ManyToManyField(Document)

    seo_data = models.ForeignKey(SeoData, on_delete=models.CASCADE)


class SiteServicesPage(models.Model):
    services = models.ManyToManyField(Article)
    seo_data = models.ForeignKey(SeoData, on_delete=models.CASCADE)


class SiteContactsPage(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = PhoneNumberField(null=True, blank=True)
    map = models.CharField(max_length=4000, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)

    seo_data = models.ForeignKey(SeoData, on_delete=models.CASCADE)


# endregion pages

# endregion SITE_CONTROL

# region PROPERTY
class House(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    house_staff = models.ManyToManyField(User)
    gallery = models.ManyToManyField(GalleryImage)


class Section(models.Model):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(House, on_delete=models.CASCADE, null=True, blank=True)


class Floor(models.Model):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)


class Account(models.Model):
    number = models.CharField(max_length=40)
    is_active = models.BooleanField()


class Flat(models.Model):
    number = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2)

    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    # tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True)

# endregion PROPERTY
