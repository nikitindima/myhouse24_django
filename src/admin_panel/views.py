from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sitemaps import ping_google
from django.db.models import Max, Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.views.generic import DeleteView, ListView, DetailView
from dateutil.utils import today

from .forms import (
    SiteHomeForm,
    SiteAboutForm,
    SiteContactsForm,
    HouseCreateForm,
    SectionForm,
    FlatCreateForm,
    FlatUpdateForm,
    UserCreateForm,
    UserUpdateForm, MeasureForm, ServiceForm, TariffForm, ServicePriceForm, UserRoleForm,
)
from .models import (
    SiteHomePage,
    SiteAboutPage,
    GalleryImage,
    Document,
    Article,
    SiteServicesPage,
    SiteContactsPage,
    House,
    Section,
    Flat, Measure, Service, Tariff,
)
from .services.forms_services import (
    validate_forms,
    save_forms,
    create_formset,
    save_extra_forms,
)
from .services.site_pages_services import (
    get_or_create_page_object,
    create_forms,
    create_formset_and_save_to_m2m_field,
    save_new_objects_to_many_to_many_field,
)
from .services.user_passes_test import site_access, house_user_access, statistics_access, flat_access, service_access, \
    tariff_access, role_access, staff_access
from ..users.models import UserRole

User = get_user_model()


@user_passes_test(statistics_access)
def home_view(request):
    return render(request, "admin_panel/pages/home.html")


# region SITE_CONTROL
@user_passes_test(site_access)
def site_home_view(request):
    obj = get_or_create_page_object(SiteHomePage)
    form1, seo_data_form = create_forms(request, obj, SiteHomeForm)
    formset = create_formset_and_save_to_m2m_field(request, obj.around_us, Article)

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


@user_passes_test(site_access)
def site_about_view(request):
    obj = get_or_create_page_object(SiteAboutPage)
    form1, seo_data_form = create_forms(request, obj, SiteAboutForm)
    formset = create_formset_and_save_to_m2m_field(request, obj.docs, Document)

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


@user_passes_test(site_access)
def site_services_view(request):
    obj = get_or_create_page_object(SiteServicesPage)
    seo_data_form = create_forms(request, obj, only_seo=True)
    formset = create_formset_and_save_to_m2m_field(request, obj.services, Article)

    if request.method == "POST":
        forms_valid_status = validate_forms(seo_data_form, formset=formset)

        if forms_valid_status:
            save_forms(seo_data_form, formset)

            for form in formset.extra_forms:
                if form.cleaned_data != {}:
                    title = form.cleaned_data.get("title")
                    description = form.cleaned_data.get("description")
                    image = form.cleaned_data.get("image")
                    new_service = Article(
                        title=title, description=description, image=image
                    )
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


@user_passes_test(site_access)
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


@user_passes_test(site_access)
def update_sitemap_view(request):
    ping_google(sitemap_url="/sitemap.xml")
    messages.success(request, "sitemap.xml был успешно обновлён!")
    return redirect(request.META.get("HTTP_REFERER", "admin_panel:site_home"))


@method_decorator(user_passes_test(site_access), name='dispatch')
class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy("admin_panel:site_services")
    success_message = "Данные успешно удалены"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(site_access), name='dispatch')
class GalleryImageDeleteView(DeleteView):
    model = GalleryImage
    success_url = reverse_lazy("admin_panel:site_about")
    success_message = "Данные успешно удалены"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(site_access), name='dispatch')
class DocumentDeleteView(DeleteView):
    model = Document
    success_url = reverse_lazy("admin_panel:site_about")
    success_message = "Данные успешно удалены"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# endregion SERVICES

# endregion SITE_CONTROL

# region PROPERTY

# region HOUSE
@method_decorator(user_passes_test(house_user_access), name='dispatch')
class HouseListView(ListView):
    template_name = "admin_panel/pages/house_list.html"
    model = House


@user_passes_test(house_user_access)
def house_create_view(request):
    errors = []
    form1 = HouseCreateForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        formset = create_formset(SectionForm, request, post=True)
        errors = formset.errors
        forms_valid_status = validate_forms(form1, formset)

        if forms_valid_status:
            house = form1.save(commit=True)

            save_extra_forms(formset, Section, house=house)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:house_list")

        messages.error(request, f"Ошибка при сохранении формы.")
        if errors:
            [
                messages.error(request, f"{field}, {error.as_text()}")
                for field, error in formset.errors[0].items()
            ]

    formset = create_formset(SectionForm, request)

    context = {
        "form1": form1,
        "formset": formset,
    }
    return render(request, "admin_panel/pages/house_create.html", context=context)


@method_decorator(user_passes_test(house_user_access), name='dispatch')
class HouseDetailView(DetailView):
    template_name = "admin_panel/pages/house_detail.html"
    model = House

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sections = Section.objects.filter(house=self.object)
        floors = sections.aggregate(Max("floors")).get("floors__max")
        context.update({"sections": sections.count(), "floors": floors})
        return context


@user_passes_test(house_user_access)
def house_update_view(request, pk):
    house = get_object_or_404(House, pk=pk)
    form1 = HouseCreateForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=house
    )
    formset = create_formset(
        SectionForm, request, post=True, qs=Section.objects.filter(house=house)
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, formset)

        if forms_valid_status:
            save_forms(form1)
            for form in formset:
                if form.cleaned_data.get("id") is not None:
                    if form.cleaned_data.get("name"):
                        form.save()

            save_extra_forms(formset, Section, house=house)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:house_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "object": house,
        "form1": form1,
        "formset": formset,
    }
    return render(request, "admin_panel/pages/house_update.html", context=context)


@method_decorator(user_passes_test(house_user_access), name='dispatch')
class HouseDeleteView(DeleteView):
    model = House
    success_url = reverse_lazy("admin_panel:house_list")
    success_message = "Дом успешно удален"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


def section_delete_view(request):
    if request.is_ajax():
        pk = request.POST["pk"]
        section = get_object_or_404(Section, pk=pk)
        section.delete()
    return JsonResponse({"success": "true"})


# endregion HOUSE

# region FLAT


@method_decorator(user_passes_test(flat_access), name='dispatch')
class FlatListView(ListView):
    template_name = "admin_panel/pages/flat_list.html"
    queryset = Flat.objects.select_related("section", "house", "owner")


@user_passes_test(flat_access)
def flat_create_view(request):
    form1 = FlatCreateForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            if request.POST.get("redirect") == "True":
                return redirect("admin_panel:flat_create")
            else:
                return redirect("admin_panel:flat_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(request, "admin_panel/pages/flat_create.html", context=context)


@method_decorator(user_passes_test(flat_access), name='dispatch')
class FlatDetailView(DetailView):
    template_name = "admin_panel/pages/flat_detail.html"
    model = Flat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@user_passes_test(flat_access)
def flat_update_view(request, pk):
    flat = get_object_or_404(Flat, pk=pk)
    form1 = FlatUpdateForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=flat
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            if request.POST.get("redirect") == "True":
                return redirect("admin_panel:flat_create")
            else:
                return redirect("admin_panel:flat_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "object": flat,
        "form1": form1,
    }
    return render(request, "admin_panel/pages/flat_update.html", context=context)


@method_decorator(user_passes_test(flat_access), name='dispatch')
class FlatDeleteView(DeleteView):
    model = Flat
    success_url = reverse_lazy("admin_panel:flat_list")
    success_message = "Квартира успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# endregion FLAT

# endregion PROPERTY

# region API


def api_sections(request, pk):
    sections = Section.objects.filter(house=pk)
    results = []

    for section in sections:
        data = section.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_floors(request, pk):
    section = get_object_or_404(Section, pk=pk)
    floors = section.floors
    results = []

    for floor in range(floors):
        data = {"id": str(range(floors)[floor] + 1), "text": f"Этаж {floor + 1}"}
        results.append(data)

    return JsonResponse({"results": results})


def api_measure_name(request):
    service_id = request.GET.get('id', None)
    service = get_object_or_404(Service, pk=service_id)

    return JsonResponse({"text": service.measure.name})


def api_users(request):
    users = User.objects.filter(status="ACTIVE")
    results = []

    for user in users:
        data = user.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_new_users(request):
    day_today = today(tzinfo=utc)
    day_week_ago = today(tzinfo=utc) - timedelta(days=7)

    users = User.objects.filter(
        status="ACTIVE", date_joined__range=[day_week_ago, day_today]
    ).order_by("-date_joined")[:10]
    results = []

    for user in users:
        data = user.serialize(pattern="api_new_users")
        results.append(data)

    return JsonResponse({"results": results})


# endregion API

# region USERS


@method_decorator(user_passes_test(house_user_access), name='dispatch')
class UserListView(ListView):
    template_name = "admin_panel/pages/user_list.html"
    # queryset = User.objects.prefetch_related('flats', 'flats__house')

    queryset = User.objects.prefetch_related(
        Prefetch("flats", queryset=Flat.objects.select_related("house"))
    ).prefetch_related("flats__house")


@user_passes_test(house_user_access)
def user_create_view(request):
    form1 = UserCreateForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:user_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(request, "admin_panel/pages/user_create.html", context=context)


@method_decorator(user_passes_test(house_user_access), name='dispatch')
class UserDetailView(DetailView):
    template_name = "admin_panel/pages/user_detail.html"
    model = User


@user_passes_test(house_user_access)
def user_update_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    form1 = UserUpdateForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=user
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:user_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "object": user,
        "form1": form1,
    }
    return render(request, "admin_panel/pages/user_update.html", context=context)


@method_decorator(user_passes_test(house_user_access), name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy("admin_panel:user_list")
    success_message = "Владелец успешно удален"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# endregion USERS

# region SYSTEM_SETTINGS

# region STAFF

@method_decorator(user_passes_test(service_access), name='dispatch')
class MeasureDeleteView(DeleteView):
    model = Measure
    success_url = reverse_lazy("admin_panel:system_services")
    success_message = "Еденица измерения успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@user_passes_test(service_access)
def check_service(request, pk):
    return JsonResponse({"result": "success"})


@user_passes_test(service_access)
def check_measure(request, pk):
    result = 'can_delete'
    measure = get_object_or_404(Measure, pk=pk)
    services = Service.objects.filter(measure=measure)
    if services.exists():
        result = 'cant_delete'

    return JsonResponse({"result": result})


@method_decorator(user_passes_test(service_access), name='dispatch')
class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy("admin_panel:system_services")
    success_message = "Услуга успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(tariff_access), name='dispatch')
class TariffDeleteView(DeleteView):
    model = Tariff
    success_url = reverse_lazy("admin_panel:system_tariffs")
    success_message = "Тариф успешно удален"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        tariff = self.get_object()
        for service_price in tariff.service_price.all():
            service_price.delete()
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# endregion STAFF


@user_passes_test(service_access)
def system_services(request):
    formset = create_formset(MeasureForm, request, post=True, qs=Measure.objects.all(), prefix='formset')
    formset2 = create_formset(ServiceForm, request, post=True, qs=Service.objects.select_related('measure'),
                              prefix='formset2')

    if request.method == "POST":
        forms_valid_status = validate_forms(formset, formset2)

        if forms_valid_status:
            save_forms(formset, formset2)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_services")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "formset": formset,
        "formset2": formset2,
    }
    return render(request, "admin_panel/pages/system_services.html", context=context)


@method_decorator(user_passes_test(tariff_access), name='dispatch')
class SystemTariffsListView(ListView):
    template_name = "admin_panel/pages/system_tariffs.html"
    model = Tariff


@user_passes_test(tariff_access)
def system_tariffs_create_view(request):
    form1 = TariffForm(request.POST or None, prefix="form1")
    formset = create_formset(ServicePriceForm, request, post=True, prefix='formset')

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, formset)

        if forms_valid_status:
            tariff = form1.save(commit=True)

            for form in formset:
                if form.cleaned_data.get("price") is not None:
                    service = form.save(commit=True)
                    tariff.service_price.add(service)
                    tariff.save()

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_tariffs")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
        "formset": formset
    }
    return render(request, "admin_panel/pages/system_tariffs_create.html", context=context)


@user_passes_test(tariff_access)
def system_tariffs_update_view(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)
    form1 = TariffForm(request.POST or None, prefix="form1", instance=tariff)
    formset = create_formset(ServicePriceForm, request, post=True, prefix='formset', qs=tariff.service_price.all())

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, formset)

        if forms_valid_status:
            save_forms(formset)
            tariff = form1.save(commit=True)

            for form in formset:
                if form.cleaned_data.get("price") is not None:
                    service = form.save(commit=True)
                    tariff.service_price.add(service)
                    tariff.save()

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_tariffs")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
        "formset": formset
    }
    return render(request, "admin_panel/pages/system_tariffs_update.html", context=context)


@user_passes_test(tariff_access)
def system_tariffs_clone_view(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)
    service_prices_copy = []

    for service_price in tariff.service_price.all():
        service_price.pk = None
        service_price._state.adding = True
        service_price.save()
        service_prices_copy.append(service_price)

    tariff.pk = None
    tariff._state.adding = True
    tariff.save()
    tariff.service_price.add(*service_prices_copy)

    return redirect('admin_panel:system_tariffs')


@method_decorator(user_passes_test(tariff_access), name='dispatch')
class TariffDetailView(DetailView):
    template_name = "admin_panel/pages/system_tariffs_detail.html"
    queryset = Tariff.objects.prefetch_related("service_price__service__measure")

# endregion SYSTEM_SETTINGS


@user_passes_test(role_access)
def system_user_role_view(request):
    qs = UserRole.objects.all()
    if not qs.exists():
        role_list = ['Директор', 'Управляющий', 'Бухгалтер', 'Электрик', 'Сантехник']
        for role in role_list:
            UserRole(name=role).save()
        qs = UserRole.objects.all()

    formset = create_formset(UserRoleForm, request, post=True, prefix='formset', qs=qs)

    if request.method == "POST":
        forms_valid_status = validate_forms(formset)
        print(formset)
        if forms_valid_status:
            save_forms(formset)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_user_roles")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "formset": formset
    }
    return render(request, "admin_panel/pages/system_user_roles.html", context=context)


@method_decorator(user_passes_test(staff_access), name='dispatch')
class StaffListView(ListView):
    queryset = User.objects.filter(is_staff=True)
    template_name = "admin_panel/pages/system_staff_list.html"
