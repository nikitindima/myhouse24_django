import os

from django.conf.global_settings import MEDIA_ROOT
from django.db import models
from django.db.models import ManyToManyField
from django.urls import reverse

from .services.media_services import UploadToPathAndRename


# region SITE_CONTROL

# region staff
class Article(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "site", "home_page", "articles")

    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    image = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )


class SeoData(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    keywords = models.CharField(max_length=2000, null=True, blank=True)


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


class GalleryImage(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "gallery-images")

    image = models.ImageField(upload_to=UploadToPathAndRename(upload_path))


class Document(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "docs")

    name = models.CharField(max_length=100)
    file = models.FileField(upload_to=UploadToPathAndRename(upload_path))


class SiteAboutPage(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "images", "portraits")

    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)
    title2 = models.CharField(max_length=100, null=True, blank=True)
    description2 = models.CharField(max_length=3000, null=True, blank=True)
    portrait = models.ImageField(upload_to=UploadToPathAndRename(upload_path), null=True, blank=True)

    gallery = ManyToManyField(GalleryImage, related_name="gallery")
    gallery2 = ManyToManyField(GalleryImage, related_name="gallery2")

    docs = ManyToManyField(Document)

    seo_data = models.ForeignKey(SeoData, on_delete=models.CASCADE)

# endregion pages

# endregion SITE_CONTROL
