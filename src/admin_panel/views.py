from django.contrib import messages
from django.contrib.sitemaps import ping_google
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .forms import SiteHomeForm, SiteAboutForm, DocumentForm, SiteContactsForm
from .models import SiteHomePage, SiteAboutPage, GalleryImage, Document, Article, SiteServicesPage, SiteContactsPage
from .services.forms_services import validate_forms, save_forms
from .services.site_pages_services import (
    get_or_create_page_object,
    create_forms,
    create_formset,
    save_new_objects_to_many_to_many_field,
)


def home_view(request):
    return render(request, "admin_panel/pages/home.html")


# region SITE_CONTROL
def site_home_view(request):
    obj = get_or_create_page_object(SiteHomePage)
    form1, seo_data_form = create_forms(request, obj, SiteHomeForm)
    formset = create_formset(request, obj.around_us, Article)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form, formset=formset)
        print(forms_valid_status, seo_data_form.errors, formset.errors)
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
    formset = create_formset(request, obj.docs, Document)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form, formset=formset)

        if forms_valid_status:
            save_forms(form1, seo_data_form, formset)
            save_new_objects_to_many_to_many_field(
                obj.gallery, "form1-gallery_upload", request
            )
            save_new_objects_to_many_to_many_field(
                obj.gallery2, "form1-gallery2_upload", request
            )
            for form in formset.extra_forms:
                if form.cleaned_data != {}:
                    name = form.cleaned_data.get("name")
                    file = form.cleaned_data.get("file")
                    new_document = Document(name=name, file=file)
                    new_document.full_clean()
                    new_document.save()
                    obj.docs.add(new_document)

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
    obj = get_or_create_page_object(SiteServicesPage)
    seo_data_form = create_forms(request, obj, only_seo=True)
    formset = create_formset(request, obj.services, Article)

    if request.method == "POST":
        forms_valid_status = validate_forms(seo_data_form, formset=formset)

        if forms_valid_status:
            save_forms(seo_data_form, formset)

            for form in formset.extra_forms:
                if form.cleaned_data != {}:
                    title = form.cleaned_data.get("title")
                    description = form.cleaned_data.get("description")
                    image = form.cleaned_data.get("image")
                    new_service = Article(title=title, description=description, image=image)
                    new_service.full_clean()
                    new_service.save()
                    obj.services.add(new_service)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:site_services")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "obj": obj,
        "seo_data_form": seo_data_form,
        "formset": formset,
    }
    return render(request, "admin_panel/pages/site_services.html", context=context)


def site_contacts_view(request):
    obj = get_or_create_page_object(SiteContactsPage)
    form1, seo_data_form = create_forms(request, obj, SiteContactsForm)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form)

        if forms_valid_status:
            save_forms(form1, seo_data_form)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:site_contacts")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "obj": obj,
        "form1": form1,
        "seo_data_form": seo_data_form,
    }
    return render(request, "admin_panel/pages/site_contacts.html", context=context)


# region SERVICES


def update_sitemap_view(request):
    ping_google(sitemap_url="/sitemap.xml")
    messages.success(request, "sitemap.xml был успешно обновлён!")
    return redirect(request.META.get("HTTP_REFERER", "admin_panel:site_home"))


class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy("admin_panel:site_services")
    success_message = "Данные успешно удалены"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class GalleryImageDeleteView(DeleteView):
    model = GalleryImage
    success_url = reverse_lazy("admin_panel:site_about")
    success_message = "Данные успешно удалены"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class DocumentDeleteView(DeleteView):
    model = Document
    success_url = reverse_lazy("admin_panel:site_about")
    success_message = "Данные успешно удалены"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# endregion SERVICES

# endregion SITE_CONTROL
