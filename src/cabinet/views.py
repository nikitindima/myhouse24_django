import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, DeleteView
from src.admin_panel.forms import UserProfileUpdateForm, CallRequestForm
from src.admin_panel.models import (
    Flat,
    Receipt,
    Account,
    Message,
    CallRequest,
    CompanyCredentials,
    Transaction,
)
from src.admin_panel.services.forms_services import validate_forms, save_forms
from src.cabinet.services.pdf_factory import PdfFactory


@login_required
def home_view(request):
    flat_id = request.GET.get("flat_id", None)

    if flat_id is None:
        user_flats_qs = Flat.objects.filter(owner=request.user)

        if user_flats_qs.exists():
            first_flat_id = user_flats_qs.order_by("id").first().id
            return redirect(reverse("cabinet:home") + f"?flat_id={str(first_flat_id)}")

        else:
            return redirect(reverse("cabinet:user_profile_detail"))

    flat = (
        Flat.objects.filter(pk=flat_id)
        .prefetch_related("flat_account__receipt_account__bill_receipt")
        .last()
    )

    queryset = (
        Receipt.objects.select_related("account__account_flat__owner")
        .prefetch_related("bill_receipt")
        .annotate(total_price=models.Sum("bill_receipt__cost"))
        .filter(account__account_flat=flat, is_passed=True)
        .order_by("-created")
    )

    transactions = Transaction.objects.select_related(
        "account", "transaction_type"
    ).filter(
        account__account_flat=flat, is_passed=True, transaction_type__type="INCOME"
    )

    balance = 0
    for receipt in queryset:
        balance -= receipt.total_price
    for transaction in transactions:
        balance += transaction.amount

    monthly_avg_summ = (
        Receipt.objects.prefetch_related("bill_receipt")
        .filter(account__account_flat=flat, is_passed=True)
        .annotate(month=TruncMonth("created"))
        .values("month")
        .annotate(monthly_summ=models.Sum("bill_receipt__cost"))
        .values("month", "monthly_summ")
        .aggregate(models.Avg("monthly_summ"))["monthly_summ__avg"]
    )

    queryset_last_month = (
        queryset.filter(
            created__lte=datetime.datetime.today(),
            created__gt=datetime.datetime.today() - datetime.timedelta(days=30),
        )
        .values("bill_receipt__service__name")
        .annotate(summ=models.Sum("bill_receipt__cost"))
        .order_by()
    )

    queryset_last_year = (
        queryset.filter(
            created__lte=datetime.datetime.today(),
            created__gt=datetime.datetime.today() - datetime.timedelta(days=365),
        )
        .values("bill_receipt__service__name")
        .annotate(summ=models.Sum("bill_receipt__cost"))
        .order_by()
    )

    monthly_summ = (
        Receipt.objects.prefetch_related("bill_receipt")
        .filter(account__account_flat=flat, is_passed=True)
        .annotate(month=TruncMonth("created"))
        .values("month")
        .annotate(monthly_summ=models.Sum("bill_receipt__cost"))
        .values("month", "monthly_summ")
    )
    if queryset_last_month.exists():
        last_month_data_json = json.dumps(
            list(queryset_last_month), cls=DjangoJSONEncoder
        )
    else:
        last_month_data_json = None

    if queryset_last_year.exists():
        last_year_data_json = json.dumps(
            list(queryset_last_year), cls=DjangoJSONEncoder
        )
    else:
        last_year_data_json = None

    if monthly_summ.exists():
        monthly_summ_json = json.dumps(list(monthly_summ), cls=DjangoJSONEncoder)
    else:
        monthly_summ_json = None

    context = {
        "current_flat_id": flat_id,
        "flat": flat,
        "queryset": queryset,
        "balance": balance,
        "monthly_avg_summ": monthly_avg_summ,
        "last_month_data_json": last_month_data_json,
        "last_year_data_json": last_year_data_json,
        "monthly_summ_json": monthly_summ_json,
    }
    return render(request, "cabinet/pages/home.html", context=context)


@login_required
def receipt_list_view(request):
    flat_id = request.GET.get("flat_id", None)

    queryset = (
        Receipt.objects.select_related("account__account_flat__owner")
        .prefetch_related("bill_receipt")
        .annotate(total_price=models.Sum("bill_receipt__cost"))
        .filter(account__account_flat__owner=request.user, is_passed=True)
        .order_by("-created")
    )

    if flat_id is not None:
        account = Account.objects.filter(account_flat__id=flat_id).first()
        queryset = queryset.filter(account=account)

    context = {"object_list": queryset, "current_flat_id_receipts": flat_id}
    return render(request, "cabinet/pages/receipt_list.html", context=context)


@method_decorator(login_required(), name="dispatch")
class ReceiptDetailView(DetailView):
    queryset = (
        Receipt.objects.select_related("account__account_flat__owner")
        .prefetch_related("bill_receipt__service__measure")
        .annotate(total_price=models.Sum("bill_receipt__cost"))
    )
    template_name = "cabinet/pages/receipt_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        receipt = kwargs["object"]
        flat_id = receipt.account.account_flat.id
        context.update({"current_flat_id_receipts": flat_id})

        return context


@login_required
def receipt_print_view(request, pk):
    receipt = (
        Receipt.objects.filter(pk=pk)
        .select_related("account__account_flat__owner")
        .prefetch_related("bill_receipt__service__measure")
        .annotate(total_price=models.Sum("bill_receipt__cost"))
        .last()
    )

    context = {
        "object": receipt,
    }
    return render(
        request, "cabinet/elements/templates/print_receipt.html", context=context
    )


@login_required
def tariff_list_view(request):
    flat_id = request.GET.get("flat_id", None)
    flat = get_object_or_404(Flat, pk=flat_id)

    queryset = flat.tariff.service_price.all().select_related("service__measure")

    context = {
        "object_list": queryset,
        "flat": flat,
        "current_flat_id_tariffs": flat_id,
    }
    return render(request, "cabinet/pages/tariff_list.html", context=context)


@method_decorator(login_required(), name="dispatch")
class MessageListView(ListView):
    template_name = "cabinet/pages/message_list.html"

    def get_queryset(self):
        user = self.request.user
        flats = Flat.objects.filter(owner=user)
        houses = flats.values("house")

        queryset = (
            Message.objects.select_related("house", "section", "flat")
            .order_by("-created")
            .filter(Q(house__in=houses) | Q(to_all=True) | Q(personal_for=user))
        )

        return queryset


@method_decorator(login_required(), name="dispatch")
class CallRequestListView(ListView):
    template_name = "cabinet/pages/call_request_list.html"

    def get_queryset(self):
        queryset = CallRequest.objects.filter(flat_owner=self.request.user)
        return queryset


@login_required()
def call_request_create_view(request):
    form1 = CallRequestForm(request.POST or None, request.FILES or None, prefix="form1")

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("cabinet:call_request_list")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "form1": form1,
    }
    return render(request, "cabinet/pages/call_request_create.html", context=context)


@method_decorator(login_required(), name="dispatch")
class CallRequestDeleteView(DeleteView):
    model = CallRequest
    success_url = reverse_lazy("cabinet:call_request_list")
    success_message = "Заявка успешно удалена"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


@login_required
def user_profile_detail_view(request):
    flats = Flat.objects.filter(owner=request.user).prefetch_related("flat_account")
    context = {"object_list": flats}
    return render(request, "cabinet/pages/user_profile_detail.html", context=context)


@login_required
def user_profile_update_view(request):
    user = request.user
    form1 = UserProfileUpdateForm(
        request.POST or None, request.FILES or None, prefix="form1", instance=user
    )

    if request.method == "POST":
        forms_valid_status = validate_forms(form1)

        if forms_valid_status:
            save_forms(form1)

            messages.success(request, "Данные успешно обновлены.")

            return redirect("cabinet:user_profile_detail")

        messages.error(request, f"Ошибка при сохранении формы.")

    context = {
        "object": user,
        "form1": form1,
    }
    return render(request, "cabinet/pages/user_profile_update.html", context=context)


@login_required
def receipt_pdf_view(request, pk):
    receipt = (
        Receipt.objects.filter(pk=pk)
        .select_related("account__account_flat__owner")
        .prefetch_related("bill_receipt")
        .annotate(total_price=models.Sum("bill_receipt__cost"))
        .order_by("-created")
        .last()
    )

    company_credentials = CompanyCredentials.objects.last()
    context = {
        "request": request,
        "receipt": receipt,
        "company_credentials": company_credentials,
        "tax_size": (receipt.total_price / 5),
        "total_summ": (receipt.total_price * 6 / 5),
    }
    return PdfFactory(
        "cabinet/elements/templates/file.html", context=context, filename="pdf_file"
    ).get_response()
