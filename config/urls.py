import allauth
from allauth.account import views as account_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from robots.models import Rule

from .sitemaps import StaticViewSitemap, robots_txt

sitemaps = {
    'static': StaticViewSitemap,
}

rule = Rule()
# url = Url(pattern='admin_panel/')
# url.save()
# rule.disallowed.add(url)


urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),

    # path("accounts/", include("allauth.urls")),
    # path("allauth/", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    # path("allauth/about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    # path("allauth/users/", include("src.users.urls", namespace="users")),
    # path("admin-old", admin.site.urls),

    # Your stuff: custom urls includes go here
    path("admin_panel/", include("src.admin_panel.urls", namespace="admin_panel")),
    path("", include("src.site.urls", namespace="site")),
    path("cabinet/", include("src.cabinet.urls", namespace="cabinet")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("accounts/login/", account_views.login, name="account_login"),
    path("accounts/signup/", account_views.signup, name="account_signup"),
    path("accounts/logout/", account_views.logout, name="account_logout"),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
