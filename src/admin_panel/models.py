import os

from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import DateRangeField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ManyToManyField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _

from .services.media_services import UploadToPathAndRename
from ..users.models import UserRole

User = get_user_model()


# region Tariff
class Measure(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name or ''


class Service(models.Model):
    name = models.CharField(max_length=100)
    is_removable = models.BooleanField(default=True)
    is_shown = models.BooleanField()
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ServicePrice(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class Tariff(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    changed = models.DateTimeField(auto_now=True)
    service_price = models.ManyToManyField(ServicePrice, related_name="service_price")

    def __str__(self):
        return self.name or ""


# endregion RECEIPTS

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
    upload_path = os.path.join(MEDIA_ROOT, "images", "houses")

    name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    house_staff = models.ManyToManyField(User)
    image1 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    image2 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    image3 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    image4 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )
    image5 = models.ImageField(
        upload_to=UploadToPathAndRename(upload_path), null=True, blank=True
    )

    def serialize(self, pattern):
        if pattern == "select2":
            return {"id": self.id, "text": self.name}

    def __str__(self):
        return self.name or ""


class Section(models.Model):
    name = models.CharField(max_length=100, blank=True)
    floors = models.PositiveIntegerField(
        blank=True, default=10, validators=[MinValueValidator(1)]
    )
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def serialize(self, pattern):
        if pattern == "select2":
            return {"id": self.id, "text": self.name}

    def __str__(self):
        return self.name or ""


class Floor(models.Model):
    name = models.CharField(max_length=100)
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, null=True, blank=True
    )


class Flat(models.Model):
    number = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2)

    floor = models.CharField(max_length=100, null=True)
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, null=True, blank=True
    )
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, null=True, related_name="houses"
    )
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="flats"
    )
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True)

    def serialize(self, pattern):
        if pattern == "select2":
            data = {"id": self.id, "text": f'{self.house.name}, кв. {self.number}'}
            return data

    def __str__(self):
        return f'{self.house.name}, кв. {self.number}'


class Account(models.Model):
    class AccountStatus(models.TextChoices):
        ACTIVE = "Active", _("Активный")
        INACTIVE = "Inactive", _("Неактивный")

    account_flat = models.OneToOneField(Flat, on_delete=models.CASCADE, related_name="flat_account")

    number = models.CharField(max_length=40, unique=True, blank=True)
    is_active = models.CharField(max_length=10, choices=AccountStatus.choices)


# endregion PROPERTY
class ReceiptTemplate(models.Model):
    upload_path = os.path.join(MEDIA_ROOT, "receipts", "templates")

    name = models.CharField(max_length=100)
    template = models.FileField(upload_to=UploadToPathAndRename(upload_path))
    is_deleted = models.BooleanField()


class Receipt(models.Model):
    is_passed = models.BooleanField()
    is_paid = models.BooleanField()
    period = DateRangeField()
    created = models.DateTimeField()

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
    services = models.ManyToManyField(Service, through='Bill')


class Bill(models.Model):
    consumption = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class MeterData(models.Model):
    number = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE)


class CompanyCredentials(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=3000, null=True, blank=True)


class TransactionType(models.Model):
    class Type(models.TextChoices):
        INCOME = "INCOME", _("Приход")
        EXPENSE = "EXPENSE", _("Расход")

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=7, choices=Type.choices)


class Transaction(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    is_passed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


class Message(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')

    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, null=True, blank=True)

    to_debtors = models.BooleanField(default=False)
    to_all = models.BooleanField(default=False)


class CallRequest(models.Model):
    description = models.CharField(max_length=3000)
    master_type = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.CharField(max_length=3000)
    status = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
