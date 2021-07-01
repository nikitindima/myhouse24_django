from django.contrib import admin

from .models import (
    SeoData,
    Article,
    SiteHomePage,
    SiteAboutPage,
    GalleryImage,
    Document, SiteServicesPage,
)

admin.site.register(SeoData)
admin.site.register(Article)
admin.site.register(SiteHomePage)
admin.site.register(SiteAboutPage)
admin.site.register(SiteServicesPage)
admin.site.register(Document)
admin.site.register(GalleryImage)
