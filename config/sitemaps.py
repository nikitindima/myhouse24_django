from django.contrib import sitemaps
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_GET


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['site:home', 'site:about', 'site:services', 'site:contacts']

    def location(self, item):
        return reverse(item)


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        f"Disallow: {reverse('admin_panel:home')}", "\n"
        f"Sitemap: {request.build_absolute_uri(reverse('django.contrib.sitemaps.views.sitemap'))}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
