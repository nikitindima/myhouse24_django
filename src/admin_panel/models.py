import os

from django.conf.global_settings import MEDIA_ROOT
from django.db import models
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

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
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

    @staticmethod
    def get_absolute_url():
        return reverse('site:home')

# endregion pages

# endregion SITE_CONTROL
