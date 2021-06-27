from django.contrib import admin

from .models import SeoData, Article, SiteHomePage

admin.site.register(SeoData)
admin.site.register(Article)
admin.site.register(SiteHomePage)
