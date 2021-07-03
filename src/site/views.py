from django.shortcuts import render
from django.views.generic import DetailView

from src.admin_panel.models import SiteHomePage, SiteAboutPage, SiteServicesPage, SiteContactsPage
from src.admin_panel.services.site_pages_services import (
    get_or_create_page_object,
)


def home_view(request):
    return render(request, "site/pages/home.html")


class HomeView(DetailView):
    template_name = "site/pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contacts = get_or_create_page_object(SiteContactsPage)

        context.update({'contacts': contacts})
        return context

    def get_object(self, queryset=None):
        obj = get_or_create_page_object(SiteHomePage)
        return obj


class AboutView(DetailView):
    template_name = "site/pages/about.html"

    def get_object(self, queryset=None):
        obj = get_or_create_page_object(SiteAboutPage)
        return obj


class ServicesView(DetailView):
    template_name = "site/pages/services.html"

    def get_object(self, queryset=None):
        obj = get_or_create_page_object(SiteServicesPage)
        return obj


class ContactsView(DetailView):
    template_name = "site/pages/contacts.html"

    def get_object(self, queryset=None):
        obj = get_or_create_page_object(SiteContactsPage)
        return obj
