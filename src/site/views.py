from django.shortcuts import render
from django.views.generic import DetailView

from src.admin_panel.models import SiteHomePage
from src.admin_panel.services.site_pages_services import (
    get_or_create_page_object,
)


def home_view(request):
    return render(request, "site/pages/home.html")


class HomeView(DetailView):
    template_name = "site/pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seo_data = context["object"].seo_data

        context.update(
            {
                "seo_data": seo_data,
            }
        )
        return context

    def get_object(self, queryset=None):
        obj = get_or_create_page_object(SiteHomePage)
        return obj


def about_view(request):
    return render(request, "site/pages/about.html")


def services_view(request):
    return render(request, "site/pages/services.html")


def contacts_view(request):
    return render(request, "site/pages/contacts.html")
