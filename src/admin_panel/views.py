from django.contrib import messages
from django.contrib.sitemaps import ping_google
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse_lazy, reverse
from django.utils.translation import get_language

from .forms import SiteHomeForm, ArticleForm, SeoDataForm
from .models import SiteHomePage, SeoData, Article
from .services.forms_services import validate_forms, save_forms
from .services.site_pages_services import get_or_create_site_home_page_obj, create_forms, \
    create_formset_for_site_home_page


def home_view(request):
    return render(request, "admin_panel/pages/home.html")


# region SITE_CONTROL
def update_sitemap_view(request):
    ping_google(sitemap_url='/sitemap.xml')
    messages.success(request, 'sitemap.xml был успешно обновлён!')
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:site_home'))


def site_home_view(request):
    obj = get_or_create_site_home_page_obj()
    form1, seo_data_form = create_forms(obj, request)
    formset = create_formset_for_site_home_page(obj, request)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form, formset)

        if forms_valid_status:
            save_forms(form1, seo_data_form, formset)
            messages.success(request, 'Данные успешно обновлены.')

            return redirect('admin_panel:site_home')

        messages.error(request, 'Ошибка при сохранении формы.')

    context = {"obj": obj, "form1": form1, 'formset': formset, 'seo_data_form': seo_data_form}
    return render(request, "admin_panel/pages/site_home.html", context=context)


def site_about_view(request):
    return render(request, "admin_panel/pages/site_about.html")


def site_services_view(request):
    return render(request, "admin_panel/pages/site_services.html")


def site_contacts_view(request):
    return render(request, "admin_panel/pages/site_contacts.html")


# endregion
