from django.contrib import messages
from django.contrib.sitemaps import ping_google
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .forms import SiteHomeForm, SiteAboutForm, DocumentForm
from .models import SiteHomePage, SiteAboutPage, GalleryImage, Document, Article
from .services.forms_services import validate_forms, save_forms
from .services.site_pages_services import (
    get_or_create_page_object,
    create_forms,
    create_formset, save_new_objects_to_many_to_many_field,
)


def home_view(request):
    return render(request, "admin_panel/pages/home.html")


# region SITE_CONTROL
def site_home_view(request):
    obj = get_or_create_page_object(SiteHomePage)
    form1, seo_data_form = create_forms(request, obj, SiteHomeForm)
    formset = create_formset(request, obj, Article)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form, formset)

        if forms_valid_status:
            save_forms(form1, seo_data_form, formset)
            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:site_home")

        messages.error(request, "Ошибка при сохранении формы.")

    context = {
        "obj": obj,
        "form1": form1,
        "formset": formset,
        "seo_data_form": seo_data_form,
    }
    return render(request, "admin_panel/pages/site_home.html", context=context)


def site_about_view(request):
    obj = get_or_create_page_object(SiteAboutPage)
    form1, seo_data_form = create_forms(request, obj, SiteAboutForm)
    formset = create_formset(request, obj, Document)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form, formset)

        if forms_valid_status:
            formset_factory = modelformset_factory(
                Document, form=DocumentForm, fields=["name", "file"], extra=0
            )
            formset = formset_factory(
                request.POST,
                request.FILES,
                prefix="formset_document",
                queryset=obj.docs.all(),
            )
            formset.is_valid()
            formset.save()
            # save_forms(form1, seo_data_form, formset)
            save_new_objects_to_many_to_many_field(obj.gallery, "form1-gallery_upload", request)
            save_new_objects_to_many_to_many_field(obj.gallery2, "form1-gallery2_upload", request)
            # save_new_objects_to_many_to_many_field(obj.docs, "formset_document-new-file", request)
            # save_new_objects_to_many_to_many_field(obj.docs, "form1-documents", request)
            # for obj in formset.cleaned_data:
            # print('post', request.POST)

            print(request.FILES)
            print('------')
            for form in formset:
                print(form.as_table())

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:site_about")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "obj": obj,
        "form1": form1,
        "seo_data_form": seo_data_form,
        "formset": formset,
    }
    return render(request, "admin_panel/pages/site_about.html", context=context)


def site_services_view(request):
    return render(request, "admin_panel/pages/site_services.html")


def site_contacts_view(request):
    return render(request, "admin_panel/pages/site_contacts.html")


def update_sitemap_view(request):
    ping_google(sitemap_url="/sitemap.xml")
    messages.success(request, "sitemap.xml был успешно обновлён!")
    return redirect(request.META.get("HTTP_REFERER", "admin_panel:site_home"))


class GalleryImageDeleteView(DeleteView):
    model = GalleryImage
    success_url = reverse_lazy("admin_panel:site_about")

# endregion
