import datetime
import json
from ast import literal_eval
from datetime import timedelta

from dateutil import rrule
from dateutil.utils import today
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.sitemaps import ping_google
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Max, Prefetch
from django.db.models import Value, Sum
from django.db.models.functions import Concat, TruncMonth
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.timezone import utc
from django.views.generic import DeleteView, ListView, DetailView

from .forms import (
    SiteHomeForm,
    SiteAboutForm,
    SiteContactsForm,
    HouseCreateForm,
    SectionForm,
    FlatCreateForm,
    FlatUpdateForm,
    UserCreateForm,
    UserUpdateForm,
    MeasureForm,
    ServiceForm,
    TariffForm,
    ServicePriceForm,
    UserRoleForm,
    StaffCreateForm,
    StaffUpdateForm,
    CredentialsForm,
    TransactionTypeForm,
    MessageForm,
    AccountCreateForm,
    AccountUpdateForm,
    TransactionIncomeCreateForm,
    TransactionExpenseCreateForm,
    MeterDataForm,
    ReceiptCreateForm,
    BillForm,
    BillUpdateForm,
    HouseStaffForm,
    CallRequestForm,
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
    Flat,
    Measure,
    Service,
    Tariff,
    CompanyCredentials,
    TransactionType,
    Message,
    Account,
    Receipt,
    Transaction,
    MeterData,
    Bill,
    HouseStaff,
    CallRequest,
)
from .services.forms_services import (
    validate_forms,
    save_forms,
    create_formset,
    save_extra_forms,
    send_form_errors_to_messages_framework,
    generate_random_number_for_model_field,
)
from .services.site_pages_services import (
    get_or_create_page_object,
    create_form_with_seo,
    create_formset_and_save_to_m2m_field,
    save_new_objects_to_many_to_many_field,
)
from .services.user_passes_test import (
    site_access,
    house_user_access,
    statistics_access,
    flat_access,
    service_access,
    tariff_access,
    role_access,
    staff_access,
    house_access,
    payments_detail_access,
    message_access,
    account_access,
    cashbox_access,
    receipt_access,
    meter_data_access,
    call_request_access,
)
from .services.xls_services import make_in_memory_worksheet
from ..users.models import UserRole
from ..users.services.user_roles_services import get_or_create_user_roles

User = get_user_model()


@staff_member_required(login_url="account_login")
def welcome_view(request):
    return render(request, "admin_panel/pages/welcome.html")


@user_passes_test(statistics_access)
def statistics_view(request):
    houses_count = House.objects.count()
    active_owners_count = User.objects.filter(
        status="ACTIVE", is_superuser=False, is_staff=False
    ).count()
    call_requests_new_count = CallRequest.objects.filter(status="NEW").count()
    call_requests_in_work_count = CallRequest.objects.filter(status="IN_WORK").count()

    flats_count = Flat.objects.count()
    accounts_count = Account.objects.filter(is_active="Active").count()

    debt_by_months_qs = Receipt.objects.select_related("account__account_flat__owner") \
        .annotate(month=TruncMonth("created")) \
        .values("month") \
        .prefetch_related("bill_receipt") \
        .annotate(total_price=models.Sum("bill_receipt__cost")) \
        .filter(is_passed=True, created__lte=datetime.datetime.today(),
                created__gt=datetime.datetime.today() - datetime.timedelta(days=365)) \
        .values('month', 'total_price') \
        .order_by('month')

    transactions_by_months = Transaction.objects.select_related("account", "transaction_type") \
        .annotate(month=TruncMonth("created")) \
        .values("month") \
        .annotate(total_price=models.Sum("amount")) \
        .filter(is_passed=True, created__lte=datetime.datetime.today(),
                created__gt=datetime.datetime.today() - datetime.timedelta(days=365),
                transaction_type__type="INCOME", created_by__isnull=False) \
        .values("month", "total_price") \
        .order_by('month')

    transactions_expense_by_month = Transaction.objects.select_related("account", "transaction_type") \
        .annotate(month=TruncMonth("created")) \
        .values("month") \
        .annotate(total_price=models.Sum("amount")) \
        .filter(is_passed=True, created__lte=datetime.datetime.today(),
                created__gt=datetime.datetime.today() - datetime.timedelta(days=365),
                transaction_type__type="EXPENSE") \
        .values("month", "total_price") \
        .order_by('month')

    end_date = datetime.datetime.today()
    start_date = (end_date - datetime.timedelta(days=365)).replace(day=1)

    receipt_data = []
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
        income_summ, debt_summ = 0, 0

        income_data = list(transactions_by_months)
        for income in income_data:
            if income['month'] == dt.date():
                income_summ = income['total_price']

        debt_data = list(debt_by_months_qs)
        for debt in debt_data:
            if debt['month'] == dt.date():
                debt_summ = debt['total_price']

        receipt_data.append({'month': dt.date(), 'debt': debt_summ, 'income': income_summ})

    receipt_data = json.dumps(receipt_data, cls=DjangoJSONEncoder)

    transactions_data = []
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
        income_summ, expense_summ = 0, 0

        income_data = list(transactions_by_months)
        for income in income_data:
            if income['month'] == dt.date():
                income_summ = income['total_price']

        expense_data = list(transactions_expense_by_month)
        for expense in expense_data:
            if expense['month'] == dt.date():
                expense_summ = expense['total_price']

        transactions_data.append({'month': dt.date(), 'expense': expense_summ, 'income': income_summ})

    transactions_data = json.dumps(transactions_data, cls=DjangoJSONEncoder)
    print(transactions_data)

    context = {
        "houses_count": houses_count,
        "active_owners_count": active_owners_count,
        "call_requests_new_count": call_requests_new_count,
        "call_requests_in_work_count": call_requests_in_work_count,
        "flats_count": flats_count,
        "accounts_count": accounts_count,
        "receipt_data": receipt_data,
        "transactions_data": transactions_data
    }
    return render(request, "admin_panel/pages/statistics.html", context=context)


# region SITE_CONTROL
@user_passes_test(site_access)
def site_home_view(request):
    obj = get_or_create_page_object(SiteHomePage)
    form1, seo_data_form = create_form_with_seo(request, obj, SiteHomeForm)
    formset = create_formset_and_save_to_m2m_field(request, obj.around_us, Article)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1, seo_data_form, formset=formset)

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
    form1, seo_data_form = create_form_with_seo(request, obj, SiteAboutForm)
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
    seo_data_form = create_form_with_seo(request, obj, only_seo=True)
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
    form1, seo_data_form = create_form_with_seo(request, obj, SiteContactsForm)

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


@method_decorator(user_passes_test(site_access), name="dispatch")
class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy("admin_panel:site_services")
    success_message = "Данные успешно удалены"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(site_access), name="dispatch")
class GalleryImageDeleteView(DeleteView):
    model = GalleryImage
    success_url = reverse_lazy("admin_panel:site_about")
    success_message = "Данные успешно удалены"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(site_access), name="dispatch")
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
@method_decorator(user_passes_test(house_access), name="dispatch")
class HouseListView(ListView):
    template_name = "admin_panel/pages/house_list.html"
    queryset = House.objects.all().order_by("-id")


@user_passes_test(house_access)
def house_create_view(request):
    errors = []
    form1 = HouseCreateForm(request.POST or None, request.FILES or None, prefix="form1")
    formset2_factory = formset_factory(HouseStaffForm, extra=0)

    if request.method == "POST":
        formset = create_formset(SectionForm, request, post=True)
        formset2 = formset2_factory(request.POST or None, prefix="house-staff")
        errors = formset.errors
        forms_valid_status = validate_forms(form1, formset, formset2)

        if forms_valid_status:
            house = form1.save(commit=True)

            for form in formset2:
                if form.cleaned_data != {}:
                    user = form.cleaned_data.get("house_staff")
                    house.house_staff.add(user)

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
    formset2 = formset2_factory(prefix="house-staff")
    context = {
        "form1": form1,
        "formset": formset,
        "formset2": formset2,
    }
    return render(request, "admin_panel/pages/house_create.html", context=context)


@method_decorator(user_passes_test(house_access), name="dispatch")
class HouseDetailView(DetailView):
    template_name = "admin_panel/pages/house_detail.html"
    model = House

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sections = Section.objects.filter(house=self.object)
        floors = sections.aggregate(Max("floors")).get("floors__max")
        context.update({"sections": sections.count(), "floors": floors})
        return context


@user_passes_test(house_access)
def house_update_view(request, pk):
    house = get_object_or_404(House, pk=pk)
    form1 = HouseCreateForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=house
    )
    formset = create_formset(
        SectionForm, request, post=True, qs=Section.objects.filter(house=house)
    )

    if request.method == "POST":
        formset2 = create_formset(
            HouseStaffForm,
            request,
            post=True,
            qs=HouseStaff.objects.filter(house=house).select_related(
                "house_staff__role"
            ),
            prefix="house-staff",
        )
        forms_valid_status = validate_forms(form1, formset, formset2)

        if forms_valid_status:
            save_forms(form1)

            for form in formset:
                if form.cleaned_data.get("id") is not None:
                    if form.cleaned_data.get("name"):
                        form.save()

            for form in formset2.extra_forms:
                user = form.cleaned_data.get("house_staff")
                house.house_staff.add(user)

            save_extra_forms(formset, Section, house=house)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:house_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    formset2 = create_formset(
        HouseStaffForm,
        request,
        qs=HouseStaff.objects.filter(house=house).select_related("house_staff__role"),
        prefix="house-staff",
    )

    context = {
        "object": house,
        "form1": form1,
        "formset": formset,
        "formset2": formset2,
    }
    return render(request, "admin_panel/pages/house_update.html", context=context)


@method_decorator(user_passes_test(house_access), name="dispatch")
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


@method_decorator(user_passes_test(flat_access), name="dispatch")
class FlatListView(ListView):
    template_name = "admin_panel/pages/flat_list.html"
    queryset = Flat.objects.select_related("section", "house", "owner").order_by("-id")


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


@method_decorator(user_passes_test(flat_access), name="dispatch")
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


@method_decorator(user_passes_test(flat_access), name="dispatch")
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
def api_house_staff_delete(request):
    staff_id = request.GET.get("staff", None)

    if staff_id is not None:
        staff = HouseStaff.objects.filter(id=staff_id)
        staff.delete()

    return JsonResponse({"results": "ok"})


def api_statistics(request):
    cash_box = Transaction.objects.select_related("transaction_type")
    cash_box_income = cash_box.filter(transaction_type__type="INCOME").aggregate(
        Sum("amount")
    )
    cash_box_expense = cash_box.filter(transaction_type__type="EXPENSE").aggregate(
        Sum("amount")
    )
    cash_box_balance = "{:,}".format(
        cash_box_income["amount__sum"] - cash_box_expense["amount__sum"]
    )

    queryset = Receipt.objects \
        .prefetch_related("bill_receipt") \
        .annotate(total_price=models.Sum("bill_receipt__cost")) \
        .filter(is_passed=True) \
        .order_by("-created")
    transactions = Transaction.objects.select_related(
        "account", "transaction_type"
    ).filter(
        is_passed=True, transaction_type__type="INCOME"
    )
    balance = 0
    for receipt in queryset:
        balance -= receipt.total_price
    for transaction in transactions:
        balance += transaction.amount
    account_balance = "{:,}".format(balance)

    debt_qs = queryset.filter(status__in=["NOT_PAID", "PARTLY_PAID"])

    debt = 0
    for receipt in debt_qs:
        debt += receipt.total_price
    account_debt = "{:,}".format(debt)

    results = {
        "cash_box_balance": cash_box_balance,
        "account_debt": account_debt,
        "account_balance": account_balance,
    }
    return JsonResponse({"results": results})


def api_houses(request):
    search = request.GET.get("search", None)
    houses = House.objects.all()

    if search is not None:
        houses = houses.filter(name__icontains=search)

    results = []

    for house_inst in houses:
        data = house_inst.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_sections(request, pk):
    search = request.GET.get("search", None)
    sections = (
        Section.objects.prefetch_related("section_flats")
            .filter(house=pk, section_flats__isnull=False)
            .distinct()
            .order_by("id")
    )
    results = []

    if search is not None:
        sections = sections.filter(name__icontains=search)

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
    service_id = request.GET.get("id", None)
    service = get_object_or_404(Service, pk=service_id)

    return JsonResponse({"text": service.measure.name})


def api_users(request):
    users = User.objects.filter(status="ACTIVE")
    results = []

    for user in users:
        data = user.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_staff(request):
    users = User.objects.filter(is_staff=True, is_superuser=False).annotate(
        user_full_name=Concat(
            "last_name", Value(" "), "first_name", Value(" "), "patronymic"
        )
    )
    results = []

    search = request.GET.get("search", None)
    if search is not None:
        users = users.filter(user_full_name__icontains=search)

    for user in users:
        data = user.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_get_staff_role(request):
    user_id = request.GET.get("user_id", None)

    if user_id is not None:
        user = (
            User.objects.filter(is_staff=True, is_superuser=False, id=user_id)
                .select_related("role")
                .last()
        )
        role = user.role.name
    else:
        role = "none"

    return JsonResponse({"results": role})


def api_flats(request):
    search = request.GET.get("search", None)
    floor = request.GET.get("floor", None)
    section_id = request.GET.get("section_id", None)
    owner_id = request.GET.get("owner_id", None)

    flats = Flat.objects.all()

    if search not in [None, ""]:
        flats = flats.filter(number__icontains=search)

    if section_id not in [None, ""]:
        flats = flats.filter(section__id=section_id)

    if floor not in [None, ""]:
        flats = flats.filter(floor=floor)

    if owner_id not in [None, ""]:
        flats = flats.filter(owner__id=owner_id)

    results = []

    for flat in flats:
        data = flat.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_master(request):
    search = request.GET.get("search", None)
    master_type_id = request.GET.get("master_type_id", None)
    flat_id = request.GET.get("flat_id", None)

    masters = (
        User.objects.filter(is_staff=True, is_superuser=False)
            .select_related("role")
            .exclude(role__name__in=["Директор", "Бухгалтер", "Управляющий"])
    )

    if flat_id not in [None, ""]:
        masters = get_object_or_404(Flat, pk=flat_id).house.house_staff.all()

    if search not in [None, ""]:
        masters = masters.filter(role__name__icontains=search)

    if master_type_id not in [None, ""]:
        masters = masters.filter(role__id=master_type_id)

    results = []

    for master in masters:
        data = master.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_master_types(request):
    search = request.GET.get("search", None)

    roles = UserRole.objects.exclude(name__in=["Директор", "Бухгалтер", "Управляющий"])

    if search not in [None, ""]:
        roles = roles.filter(name__icontains=search)

    results = []

    for role in roles:
        data = role.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_delete_messages(request):
    id_list = literal_eval(request.GET.get("id_list", None))
    Message.objects.filter(pk__in=id_list).delete()
    return JsonResponse({"results": "Success"})


def api_delete_receipts(request):
    id_list = literal_eval(request.GET.get("id_list", None))
    Receipt.objects.filter(pk__in=id_list).delete()
    return JsonResponse({"results": "Success"})


def api_get_services_from_tariff(request):
    tariff_id = request.GET.get("tariff_id", None)

    if tariff_id not in ["", None]:
        tariff = get_object_or_404(Tariff, pk=tariff_id)
        services = tariff.service_price.select_related("service__measure")
        data = serialize("json", services)
        results = json.loads(data)
    else:
        results = "none"

    return JsonResponse({"results": results})


def api_get_meter_data(request):
    service_id = request.GET.get("service_id", None)
    flat_id = request.GET.get("flat_id", None)

    if service_id not in ["", None] and flat_id not in ["", None]:
        service = get_object_or_404(Service, pk=service_id)
        flat = get_object_or_404(Flat, pk=flat_id)
        meter_data = MeterData.objects.filter(service=service, flat=flat, status="NEW")
        if meter_data.exists():
            results = meter_data.last().amount
        else:
            results = "none"
    else:
        results = "none"

    return JsonResponse({"results": results})


def api_new_users(request):
    day_today = datetime.datetime.now(tz=utc)
    day_week_ago = today(tzinfo=utc) - timedelta(days=7)

    users = User.objects.filter(
        status="ACTIVE", date_joined__range=[day_week_ago, day_today]
    ).order_by("-date_joined")[:10]
    results = []

    for user in users:
        data = user.serialize(pattern="api_new_users")
        results.append(data)

    return JsonResponse({"results": results})


def api_get_owner(request):
    flat_id = request.GET.get("flat_id", None)

    if flat_id is not None:
        flat = get_object_or_404(Flat, pk=flat_id)
        owner = flat.owner

    else:
        raise Exception("Function api_accounts does not get user_id or flat_id")

    results = {"id": str(owner.id), "name": owner.full_name, "phone": str(owner.phone)}
    print(results)
    return JsonResponse({"results": results})


def api_accounts(request):
    user_id = request.GET.get("user_id", None)
    flat_id = request.GET.get("flat_id", None)
    results = []

    if user_id is not None:
        user = get_object_or_404(User, pk=user_id)
        accounts = Account.objects.select_related("account_flat__owner").filter(
            account_flat__owner=user
        )

    elif flat_id is not None:
        flat = get_object_or_404(Flat, pk=flat_id)
        accounts = Account.objects.select_related("account_flat__owner").filter(
            account_flat=flat
        )

    else:
        raise Exception("Function api_accounts does not get user_id or flat_id")

    for account in accounts:
        data = account.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


def api_transaction_types(request):
    trans_type = request.GET.get("trans_type", None)
    trans_type_qs = TransactionType.objects.filter(type=trans_type)
    results = []

    for trans_type in trans_type_qs:
        data = trans_type.serialize(pattern="select2")
        results.append(data)

    return JsonResponse({"results": results})


# def api_meter_data_by_flat(request):
#     flat_id = request.GET.get('flat_id', None)
#     results = []
#     queryset = MeterData.objects.select_related('service', 'flat__house', 'flat__section',
#                                                 'service__measure').order_by('-id')
#
#     if flat_id is not None:
#         flat = get_object_or_404(Flat, pk=flat_id)
#         queryset = queryset.filter(flat=flat)

# for object in queryset:
#     data = {
#         'number': object.number
#     }

# return JsonResponse({"results": queryset})
# endregion API

# region USERS


@method_decorator(user_passes_test(house_user_access), name="dispatch")
class UserListView(ListView):
    template_name = "admin_panel/pages/user_list.html"
    # queryset = User.objects.prefetch_related('flats', 'flats__house')

    queryset = (
        User.objects.filter(is_staff=False, is_superuser=False)
            .prefetch_related(
            Prefetch("flats", queryset=Flat.objects.select_related("house"))
        )
            .prefetch_related("flats__house")
            .order_by("-date_joined")
    )


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


@method_decorator(user_passes_test(house_user_access), name="dispatch")
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


@method_decorator(user_passes_test(house_user_access), name="dispatch")
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


@method_decorator(user_passes_test(service_access), name="dispatch")
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
    result = "can_delete"
    measure = get_object_or_404(Measure, pk=pk)
    services = Service.objects.filter(measure=measure)
    if services.exists():
        result = "cant_delete"

    return JsonResponse({"result": result})


@method_decorator(user_passes_test(service_access), name="dispatch")
class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy("admin_panel:system_services")
    success_message = "Услуга успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(tariff_access), name="dispatch")
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
    formset = create_formset(
        MeasureForm, request, post=True, qs=Measure.objects.all(), prefix="formset"
    )
    formset2 = create_formset(
        ServiceForm,
        request,
        post=True,
        qs=Service.objects.select_related("measure"),
        prefix="formset2",
    )

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


@method_decorator(user_passes_test(tariff_access), name="dispatch")
class SystemTariffsListView(ListView):
    template_name = "admin_panel/pages/system_tariffs_list.html"
    queryset = Tariff.objects.all().order_by("-id")


@user_passes_test(tariff_access)
def system_tariffs_create_view(request):
    form1 = TariffForm(request.POST or None, prefix="form1")
    formset = create_formset(ServicePriceForm, request, post=True, prefix="formset")

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

    context = {"form1": form1, "formset": formset}
    return render(
        request, "admin_panel/pages/system_tariffs_create.html", context=context
    )


@user_passes_test(tariff_access)
def system_tariffs_update_view(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)
    form1 = TariffForm(request.POST or None, prefix="form1", instance=tariff)
    formset = create_formset(
        ServicePriceForm,
        request,
        post=True,
        prefix="formset",
        qs=tariff.service_price.all(),
    )

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

    context = {"form1": form1, "formset": formset}
    return render(
        request, "admin_panel/pages/system_tariffs_update.html", context=context
    )


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

    return redirect("admin_panel:system_tariffs")


@method_decorator(user_passes_test(tariff_access), name="dispatch")
class TariffDetailView(DetailView):
    template_name = "admin_panel/pages/system_tariffs_detail.html"
    queryset = Tariff.objects.prefetch_related("service_price__service__measure")


# endregion SYSTEM_SETTINGS


@user_passes_test(role_access)
def system_user_role_view(request):
    qs = get_or_create_user_roles()
    formset = create_formset(UserRoleForm, request, post=True, prefix="formset", qs=qs)

    if request.method == "POST":
        forms_valid_status = validate_forms(formset)

        if forms_valid_status:
            save_forms(formset)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_staff_roles")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {"formset": formset}
    return render(request, "admin_panel/pages/system_staff_roles.html", context=context)


@method_decorator(user_passes_test(staff_access), name="dispatch")
class StaffListView(ListView):
    queryset = User.objects.filter(is_staff=True, is_superuser=False).order_by(
        "-date_joined"
    )
    template_name = "admin_panel/pages/system_staff_list.html"


@user_passes_test(staff_access)
def staff_create_view(request):
    form1 = StaffCreateForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            staff_user = form1.save()
            staff_user.is_staff = True
            staff_user.save()

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:system_staff_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(
        request, "admin_panel/pages/system_staff_create.html", context=context
    )


@method_decorator(user_passes_test(staff_access), name="dispatch")
class StaffDeleteView(DeleteView):
    queryset = User.objects.filter(is_staff=True, is_superuser=False)
    success_url = reverse_lazy("admin_panel:system_staff_list")
    success_message = "Пользователь успешно удален"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@user_passes_test(staff_access)
def staff_update_view(request, pk):
    user = get_object_or_404(
        User.objects.filter(is_staff=True, is_superuser=False), pk=pk
    )
    form1 = StaffUpdateForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=user
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            staff_user = form1.save()
            staff_user.save()

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_staff_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(
        request, "admin_panel/pages/system_staff_update.html", context=context
    )


@method_decorator(user_passes_test(staff_access), name="dispatch")
class StaffDetailView(DetailView):
    template_name = "admin_panel/pages/system_staff_detail.html"
    queryset = User.objects.filter(is_staff=True, is_superuser=False)


@user_passes_test(staff_access)
def credentials_update_view(request):
    obj = CompanyCredentials.objects.last()
    if obj is None:
        obj = CompanyCredentials()
        obj.save()

    form1 = CredentialsForm(request.POST or None, prefix="form1", instance=obj)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)
            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_credentials")

        messages.error(request, "Ошибка при сохранении формы.")

    context = {
        "obj": obj,
        "form1": form1,
    }
    return render(request, "admin_panel/pages/system_credentials.html", context=context)


@method_decorator(user_passes_test(payments_detail_access), name="dispatch")
class TransactionTypeListView(ListView):
    model = TransactionType
    template_name = "admin_panel/pages/system_transaction_type_list.html"


@user_passes_test(payments_detail_access)
def transaction_type_create_view(request):
    form1 = TransactionTypeForm(
        request.POST or None, request.FILES or None, prefix="form1"
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:system_transaction_type_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(
        request,
        "admin_panel/pages/system_transaction_type_create.html",
        context=context,
    )


@user_passes_test(payments_detail_access)
def transaction_type_update_view(request, pk):
    transaction_type = get_object_or_404(TransactionType, pk=pk)
    form1 = TransactionTypeForm(
        request.POST or None, prefix="form1", instance=transaction_type
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:system_transaction_type_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(
        request,
        "admin_panel/pages/system_transaction_type_update.html",
        context=context,
    )


@method_decorator(user_passes_test(message_access), name="dispatch")
class MessageListView(ListView):
    queryset = Message.objects.select_related("house", "section", "flat").order_by(
        "-created"
    )
    template_name = "admin_panel/pages/message_list.html"


@user_passes_test(message_access)
def message_create_view(request):
    form1 = MessageForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            title = form1.cleaned_data.get("title")
            description = form1.cleaned_data.get("description")
            to_debtors = form1.cleaned_data.get("to_debtors")
            house_inst = form1.cleaned_data.get("house")
            section = form1.cleaned_data.get("section")
            floor = form1.cleaned_data.get("floor")
            flat_pk = form1.cleaned_data.get("flat")
            if flat_pk != "0" and flat_pk != "":
                flat = get_object_or_404(Flat, pk=flat_pk)
            else:
                flat = None
            floor = None if floor == 0 else floor

            message = Message(
                title=title,
                description=description,
                created_by=request.user,
                house=house_inst,
                section=section,
                floor=floor,
                flat=flat,
                to_debtors=to_debtors,
            )

            if house_inst is None:
                message.to_all = True

            message.save()

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:message_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(request, "admin_panel/pages/message_create.html", context=context)


@method_decorator(user_passes_test(account_access), name="dispatch")
class AccountListView(ListView):
    queryset = Account.objects.select_related(
        "account_flat",
        "account_flat__house",
        "account_flat__owner",
        "account_flat__section",
    ).prefetch_related("receipt_account").annotate(
        expense=models.Sum("receipt_account__bill_receipt__cost"),
    )
    template_name = "admin_panel/pages/account_list.html"


@user_passes_test(account_access)
def account_create_view(request):
    form1 = AccountCreateForm(
        request.POST or None, request.FILES or None, prefix="form1"
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            number = form1.cleaned_data.get("number")
            is_active = form1.cleaned_data.get("is_active")
            flat_id = form1.cleaned_data.get("flat")
            flat = get_object_or_404(Flat, pk=flat_id)

            account = Account(account_flat=flat, number=number, is_active=is_active)
            account.save()

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:account_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(request, "admin_panel/pages/account_create.html", context=context)


@method_decorator(user_passes_test(account_access), name="dispatch")
class AccountDeleteView(DeleteView):
    model = Account
    success_url = reverse_lazy("admin_panel:account_list")
    success_message = "Счёт успешно удален"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@user_passes_test(account_access)
def account_update_view(request, pk):
    account = get_object_or_404(Account, pk=pk)
    flat = Flat.objects.filter(flat_account=pk).select_related(
        "section", "house", "owner"
    )[0]

    form1 = AccountUpdateForm(request.POST or None, prefix="form1", instance=account)

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            flat_id = form1.cleaned_data.get("flat")
            flat = get_object_or_404(Flat, pk=flat_id)

            save_forms(form1)
            account.account_flat = flat
            account.save()

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:account_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
        "flat": flat,
    }
    return render(request, "admin_panel/pages/account_update.html", context=context)


@method_decorator(user_passes_test(account_access), name="dispatch")
class AccountDetailView(DetailView):
    template_name = "admin_panel/pages/account_detail.html"
    queryset = Account.objects.select_related(
        "account_flat", "account_flat__house", "account_flat__section"
    )


@user_passes_test(account_access)
def account_xls_list(request):
    columns = ["№", "Статус", "Квартира", "Дом", "Секция", "Владелец", "Остаток"]
    cell_format, output, workbook, worksheet = make_in_memory_worksheet(columns)

    queryset = Account.objects.select_related(
        "account_flat",
        "account_flat__house",
        "account_flat__section",
        "account_flat__owner",
    )

    row = 1
    for obj in queryset.iterator():
        worksheet.write(row, 0, obj.number, cell_format)
        worksheet.write(row, 1, obj.is_active, cell_format)
        worksheet.write(row, 2, obj.account_flat.number, cell_format)
        worksheet.write(row, 3, obj.account_flat.house.__str__(), cell_format)
        worksheet.write(row, 4, obj.account_flat.section.__str__(), cell_format)
        worksheet.write(row, 5, obj.account_flat.owner.__str__(), cell_format)
        worksheet.write(row, 6, "TODO", cell_format)
        row += 1

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = "attachment; filename=account_data.xlsx"

    output.close()

    return response


@method_decorator(user_passes_test(cashbox_access), name="dispatch")
class TransactionListView(ListView):
    template_name = "admin_panel/pages/transaction_list.html"

    def get_queryset(self):
        account_id = self.request.GET.get("account_id", None)
        if account_id is not None:
            queryset = Transaction.objects.select_related(
                "account__account_flat__owner", "receipt", "transaction_type", "created_by") \
                .order_by("-created").filter(account__id=account_id)
        else:
            queryset = Transaction.objects.select_related(
                "account__account_flat__owner", "receipt", "transaction_type", "created_by").order_by("-created")
        return queryset


@method_decorator(user_passes_test(cashbox_access), name="dispatch")
class TransactionDetailView(DetailView):
    template_name = "admin_panel/pages/transaction_detail.html"
    queryset = Transaction.objects.select_related('created_by', 'account', 'manager')


@user_passes_test(cashbox_access)
def transaction_income_create_view(request):
    transaction_id = request.GET.get("transaction_id", None)
    account_id = request.GET.get("account_id", None)
    number = generate_random_number_for_model_field(model=Transaction, field="number", length=8)
    form1 = TransactionIncomeCreateForm(request.POST or None, prefix="form1",
                                        initial={'number': number, 'created': today()})

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:transaction_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    if transaction_id is not None:
        obj = get_object_or_404(Transaction, pk=transaction_id)

        form1.initial = {
            "created_by": obj.created_by,
            "is_passed": obj.is_passed,
            "manager": obj.manager,
            "amount": obj.amount,
            "account": obj.account,
            "created": today(),
            "number": number,
            "transaction_type": obj.transaction_type,
            "description": obj.description,
        }
    elif account_id is not None:
        obj = Account.objects.filter(pk=account_id) \
            .select_related('account_flat__owner').last()

        form1.initial = {
            "created_by": obj.account_flat.owner,
            "is_passed": True,
            "manager": User.objects.filter(is_staff=True, is_superuser=False).last(),
            "account": obj.account_flat,
            "created": today(),
            "number": number,
        }

    context = {
        "form1": form1,
    }
    return render(
        request, "admin_panel/pages/transaction_income_create.html", context=context
    )


@user_passes_test(cashbox_access)
def transaction_expense_create_view(request):
    transaction_id = request.GET.get("transaction_id", None)
    number = generate_random_number_for_model_field(model=Transaction, field="number", length=8)
    form1 = TransactionExpenseCreateForm(request.POST or None, initial={'number': number}, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:transaction_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    if transaction_id is not None:
        obj = Transaction.objects.filter(id=transaction_id).last()

        form1.initial = {
            "is_passed": obj.is_passed,
            "manager": obj.manager,
            "amount": obj.amount,
            "created": today(),
            "number": number,
            "transaction_type": obj.transaction_type,
            "description": obj.description,
        }

    context = {
        "form1": form1,
    }
    return render(
        request, "admin_panel/pages/transaction_expense_create.html", context=context
    )


@method_decorator(user_passes_test(cashbox_access), name="dispatch")
class TransactionDeleteView(DeleteView):
    model = Transaction
    success_url = reverse_lazy("admin_panel:transaction_list")
    success_message = "Ведомость успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@user_passes_test(payments_detail_access)
def transaction_update_view(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if transaction.transaction_type.type == "EXPENSE":
        form1 = TransactionExpenseCreateForm(
            request.POST or None, prefix="form1", instance=transaction
        )
    else:
        form1 = TransactionIncomeCreateForm(
            request.POST or None, prefix="form1", instance=transaction
        )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:transaction_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(request, "admin_panel/pages/transaction_update.html", context=context)


@user_passes_test(account_access)
def transaction_detail_xls(request, pk):
    columns = []
    cell_format, output, workbook, worksheet = make_in_memory_worksheet(columns)

    obj = Transaction.objects.filter(pk=pk).select_related(
        "account__account_flat__owner", "receipt", "transaction_type", "created_by"
    ).last()

    transaction_type = "Приход" if obj.transaction_type.type == "INCOME" else "Расход"
    status = "Проведена" if obj.is_passed is True else "Не проведена"
    data = [
        {"row_name": "Платеж", "row_data": f"#{obj.number}"},
        {"row_name": "Дата", "row_data": f"{str(obj.created)}"},
        {"row_name": "Владелец квартиры", "row_data": f"{obj.created_by.full_name}"},
        {"row_name": "Лицевой счет", "row_data": f"{obj.account.number}"},
        {"row_name": "Приход/Расход", "row_data": f"{transaction_type}"},
        {"row_name": "Статус", "row_data": f"{status}"},
        {"row_name": "Статья", "row_data": f"{obj.transaction_type.name}"},
        {"row_name": "Квитанция", "row_data": "-"},
        {"row_name": "Услуга", "row_data": "-"},
        {"row_name": "Сумма", "row_data": f"{obj.amount}"},
        {"row_name": "Валюта", "row_data": "грн."},
        {"row_name": "Комментарий", "row_data": f"{obj.description}"},
        {"row_name": "Менеджер", "row_data": f"{obj.manager.full_name}"},
    ]
    for row in range(len(data)):
        worksheet.write(row, 0, data[row]['row_name'], cell_format)
        worksheet.write(row, 1, data[row]['row_data'], cell_format)

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = "attachment; filename=transaction_detail.xlsx"

    output.close()

    return response


@user_passes_test(account_access)
def transaction_list_xls(request):
    columns = [
        "№",
        "Дата",
        "Статус",
        "Тип платежа",
        "Владелец",
        "Лицевой счет",
        "Приход/Расход",
        "Сумма (грн)",
    ]
    cell_format, output, workbook, worksheet = make_in_memory_worksheet(columns)

    queryset = Transaction.objects.select_related(
        "account__account_flat__owner", "receipt", "transaction_type", "created_by"
    ).order_by("-created")

    row = 1
    for obj in queryset.iterator():
        is_passed = "Проведена" if obj.is_passed == 1 else "Не проведена"
        account_number = obj.account.number if obj.account is not None else "-"
        worksheet.write(row, 0, obj.number, cell_format)
        worksheet.write(row, 1, obj.created, cell_format)
        worksheet.write(row, 2, is_passed, cell_format)
        worksheet.write(row, 3, obj.transaction_type.name, cell_format)
        worksheet.write(row, 4, obj.created_by.__str__(), cell_format)
        worksheet.write(row, 5, account_number, cell_format)
        worksheet.write(row, 6, obj.transaction_type.type, cell_format)
        worksheet.write(row, 7, obj.amount, cell_format)
        row += 1

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = "attachment; filename=account_data.xlsx"

    output.close()

    return response


@method_decorator(user_passes_test(meter_data_access), name="dispatch")
class MeterDataListView(ListView):
    queryset = MeterData.objects.select_related(
        "service", "flat__house", "flat__section", "service__measure"
    ).order_by("-id")
    template_name = "admin_panel/pages/meter_data_list.html"


@method_decorator(user_passes_test(meter_data_access), name="dispatch")
class MeterDataByFlatListView(ListView):
    template_name = "admin_panel/pages/meter_data_list_by_flat.html"

    def get_queryset(self):
        flat_id = self.request.GET.get("flat_id", None)
        queryset = MeterData.objects.select_related(
            "service", "flat__house", "flat__section", "service__measure"
        ).order_by("-id")
        if flat_id is not None:
            flat = get_object_or_404(Flat, pk=flat_id)
            queryset = queryset.filter(flat=flat)
            self.extra_context = {"flat": flat}
        return queryset


@user_passes_test(meter_data_access)
def meter_data_create_view(request):
    meter_data_id = request.GET.get("meter_data_id", None)
    form1_initial = None

    if request.method == "POST":
        form1 = MeterDataForm(request.POST or None, prefix="form1")
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:meter_data_list")

        messages.error(request, f"Ошибка при сохранении формы.")
        send_form_errors_to_messages_framework(form1, request)

    number = generate_random_number_for_model_field(
        model=MeterData, field="number", length=8
    )
    form1 = MeterDataForm(initial={"number": number}, prefix="form1")

    if meter_data_id is not None:
        obj = MeterData.objects.filter(id=meter_data_id).select_related(
            "service", "flat__house", "flat__section", "service__measure"
        )[0]

        form1.initial = {
            "flat": obj.flat,
            "status": obj.status,
            "service": obj.service,
            "created": today(),
            "number": number,
        }
        form1_initial = {
            "house": {"id": obj.flat.house.id, "text": obj.flat.house.name},
            "section": {"id": obj.flat.section.id, "text": obj.flat.section.name},
        }

    context = {"form1": form1, "form1_initial": form1_initial}
    return render(request, "admin_panel/pages/meter_data_create.html", context=context)


@method_decorator(user_passes_test(meter_data_access), name="dispatch")
class MeterDataDeleteView(DeleteView):
    model = MeterData
    success_url = reverse_lazy("admin_panel:meter_data_list")
    success_message = "Показание счетчика успешно удалены"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@user_passes_test(meter_data_access)
def meter_data_update_view(request, pk):
    obj = MeterData.objects.filter(pk=pk).select_related(
        "service", "flat__house", "flat__section", "service__measure"
    )[0]
    form1 = MeterDataForm(request.POST or None, prefix="form1", instance=obj)

    if request.method == "POST":

        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:meter_data_list")

        messages.error(request, f"Ошибка при сохранении формы.")
        send_form_errors_to_messages_framework(form1, request)

    form1_initial = {
        "house": {"id": obj.flat.house.id, "text": obj.flat.house.name},
        "section": {"id": obj.flat.section.id, "text": obj.flat.section.name},
    }

    context = {"form1": form1, "form1_initial": form1_initial}
    return render(request, "admin_panel/pages/meter_data_create.html", context=context)


@method_decorator(user_passes_test(receipt_access), name="dispatch")
class ReceiptListView(ListView):
    template_name = "admin_panel/pages/receipt_list.html"

    def get_queryset(self):
        account_id = self.request.GET.get("account_id", None)
        if account_id is not None:
            queryset = Receipt.objects.filter(account__id=account_id) \
                .select_related("account__account_flat__owner") \
                .prefetch_related("bill_receipt") \
                .annotate(total_price=models.Sum("bill_receipt__cost")) \
                .order_by("-created")
        else:
            queryset = Receipt.objects\
                .select_related("account__account_flat__owner") \
                .prefetch_related("bill_receipt") \
                .annotate(total_price=models.Sum("bill_receipt__cost")) \
                .order_by("-created")
        return queryset


@user_passes_test(receipt_access)
def receipt_create_view(request):
    receipt_id = request.GET.get("receipt_id", None)
    account_id = request.GET.get("account_id", None)
    receipt, owner = None, None

    number = generate_random_number_for_model_field(
        model=Receipt, field="number", length=8
    )
    form1_initial = {"number": number, "created": today()}

    formset = create_formset(
        BillForm, request, post=True, prefix="formset", can_delete=True
    )
    meter_data_qs = MeterData.objects.select_related(
        "service", "flat__house", "flat__section", "service__measure"
    ).order_by("-id")

    if receipt_id is not None:
        receipt = get_object_or_404(Receipt, pk=receipt_id)
        flat = receipt.account.account_flat
        account = receipt.account
        bills = Bill.objects.filter(receipt=receipt)
        formset.queryset = bills
        form1_initial.update(
            {
                "is_passed": receipt.is_passed,
                "created": today(),
                "account": receipt.account,
                "tariff": receipt.tariff,
                "status": receipt.status,
                "period_start": receipt.period_start,
                "period_end": receipt.period_end,
            }
        )
        owner = receipt.account.account_flat.owner
        meter_data_qs = meter_data_qs.filter(flat=flat)

    elif account_id is not None:
        account = Account.objects.filter(pk=account_id).last()

        form1_initial.update(
            {
                "is_passed": True,
                "created": today(),
                "account": account,
                "tariff": Tariff.objects.last(),
                "status": "NOT_PAID",
                "period_start": today(),
                "period_end": today(),
            }
        )

        owner = account.account_flat.owner
        meter_data_qs = meter_data_qs.filter(flat=account.account_flat)

    if request.method == "POST":
        form1 = ReceiptCreateForm(request.POST, prefix="form1")
        forms_valid_status = validate_forms(form1, formset)

        if forms_valid_status:
            receipt = form1.save()

            for form in formset:
                consumption = form.cleaned_data.get("consumption")
                price = form.cleaned_data.get("price")
                cost = form.cleaned_data.get("cost")
                service = form.cleaned_data.get("service")

                if all(
                        [
                            consumption is not None,
                            price is not None,
                            service is not None,
                            cost is not None,
                        ]
                ):
                    bill = Bill(
                        consumption=consumption,
                        price=price,
                        cost=cost,
                        service=service,
                        receipt=receipt,
                    )
                    bill.save()

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:receipt_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    form1 = ReceiptCreateForm(initial=form1_initial, prefix="form1")

    context = {
        "form1": form1,
        "formset": formset,
        "meter_data_qs": meter_data_qs,
        "account": account,
        "owner": owner,
    }

    return render(request, "admin_panel/pages/receipt_create.html", context=context)


@user_passes_test(receipt_access)
def receipt_update_view(request, pk):
    receipt = (
        Receipt.objects.filter(pk=pk)
            .select_related(
            "account__account_flat__house",
            "account__account_flat__section",
            "account__account_flat__owner",
        )
            .last()
    )
    flat = receipt.account.account_flat
    owner = flat.owner
    bills = Bill.objects.filter(receipt=receipt)

    formset = create_formset(
        BillUpdateForm, request, post=True, prefix="formset", qs=bills, can_delete=True
    )
    meter_data_qs = (
        MeterData.objects.filter(flat=flat)
            .select_related("service", "flat__house", "flat__section", "service__measure")
            .order_by("-id")
    )

    if request.method == "POST":
        form1 = ReceiptCreateForm(request.POST, prefix="form1", instance=receipt)
        forms_valid_status = validate_forms(form1, formset)

        if forms_valid_status:
            save_forms(form1, formset)

            messages.success(request, "Данные успешно cохранены.")

            return redirect("admin_panel:receipt_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    form1 = ReceiptCreateForm(prefix="form1", instance=receipt)

    context = {
        "form1": form1,
        "formset": formset,
        "meter_data_qs": meter_data_qs,
        "receipt": receipt,
        "owner": owner,
    }
    return render(request, "admin_panel/pages/receipt_update.html", context=context)


@method_decorator(user_passes_test(receipt_access), name="dispatch")
class ReceiptDeleteView(DeleteView):
    model = Receipt
    success_url = reverse_lazy("admin_panel:receipt_list")
    success_message = "Квитанции успешно удалены"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(call_request_access), name="dispatch")
class CallRequestListView(ListView):
    model = CallRequest
    template_name = "admin_panel/pages/call_request_list.html"


@user_passes_test(call_request_access)
def call_request_create_view(request):
    form1 = CallRequestForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:call_request_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(
        request, "admin_panel/pages/call_request_create.html", context=context
    )


@user_passes_test(call_request_access)
def call_request_update_view(request, pk):
    call_request = get_object_or_404(CallRequest, pk=pk)
    form1 = CallRequestForm(
        request.POST or None,
        request.FILES or None,
        prefix="form1",
        instance=call_request,
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("admin_panel:call_request_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(
        request, "admin_panel/pages/call_request_update.html", context=context
    )


@method_decorator(login_required(), name="dispatch")
class CallRequestDeleteView(DeleteView):
    model = CallRequest
    success_url = reverse_lazy("admin_panel:call_request_list")
    success_message = "Заявка успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@method_decorator(user_passes_test(account_access), name="dispatch")
class CallRequestDetailView(DetailView):
    queryset = CallRequest.objects.all()
    template_name = "admin_panel/pages/call_request_detail.html"
