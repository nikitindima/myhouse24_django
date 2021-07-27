import io
import os

import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
# (login_url='account_login')
from django.urls import reverse
from django.views.generic import DetailView, ListView
from openpyxl import Workbook
from reportlab.pdfgen import canvas

from config import settings
from src.admin_panel.forms import ReceiptCreateForm, UserUpdateForm, UserProfileUpdateForm
from src.admin_panel.models import Flat, Receipt, Account, Bill, Tariff, ServicePrice, Message, CallRequest, \
    CompanyCredentials
from src.admin_panel.services.forms_services import validate_forms, save_forms
from src.admin_panel.services.xls_services import make_in_memory_worksheet
from src.cabinet.services.pdf_factory import PdfFactory


@login_required
def home_view(request):
    flat_id = request.GET.get('flat_id', None)
    if flat_id is None:
        first_flat_id = Flat.objects.filter(owner=request.user).order_by('id').first().id
        return redirect(reverse('cabinet:home') + f'?flat_id={str(first_flat_id)}')

    context = {
        'current_flat_id': flat_id
    }
    return render(request, "cabinet/pages/home.html", context=context)


def receipt_list_view(request):
    flat_id = request.GET.get('flat_id', None)

    queryset = Receipt.objects.select_related('account__account_flat__owner').prefetch_related('bill_receipt') \
        .annotate(total_price=models.Sum('bill_receipt__cost')).filter(
        account__account_flat__owner=request.user, is_passed=True).order_by('-created')

    if flat_id is not None:
        account = Account.objects.filter(account_flat__id=flat_id).first()
        queryset = queryset.filter(account=account)

    context = {
        'object_list': queryset,
        'current_flat_id_receipts': flat_id
    }
    return render(request, "cabinet/pages/receipt_list.html", context=context)


class ReceiptDetailView(DetailView):
    queryset = Receipt.objects.select_related('account__account_flat__owner').prefetch_related(
        'bill_receipt__service__measure') \
        .annotate(total_price=models.Sum('bill_receipt__cost'))
    template_name = "cabinet/pages/receipt_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        receipt = kwargs['object']
        flat_id = receipt.account.account_flat.id
        context.update({"current_flat_id_receipts": flat_id})

        return context


def receipt_print_view(request, pk):
    receipt = Receipt.objects.filter(pk=pk) \
        .select_related('account__account_flat__owner') \
        .prefetch_related('bill_receipt__service__measure') \
        .annotate(total_price=models.Sum('bill_receipt__cost')).last()

    context = {
        'object': receipt,
    }
    return render(request, "cabinet/elements/templates/print_receipt.html", context=context)


def tariff_list_view(request):
    flat_id = request.GET.get('flat_id', None)
    flat = get_object_or_404(Flat, pk=flat_id)

    queryset = flat.tariff.service_price.all().select_related('service__measure')

    context = {
        'object_list': queryset,
        'flat': flat,
        'current_flat_id_tariffs': flat_id
    }
    return render(request, "cabinet/pages/tariff_list.html", context=context)


class MessageListView(ListView):
    template_name = "cabinet/pages/message_list.html"

    def get_queryset(self):
        user = self.request.user
        flats = Flat.objects.filter(owner=user)
        houses = flats.values('house')
        debtor = False

        queryset = Message.objects. \
            select_related('house', 'section', 'flat').order_by('-created'). \
            filter(Q(house__in=houses) | Q(to_all=True))

        return queryset


class CallRequestListView(ListView):
    template_name = "cabinet/pages/call_request_list.html"

    def get_queryset(self):
        queryset = CallRequest.objects.filter(flat_owner=self.request.user)
        return queryset


def user_profile_detail_view(request):
    flats = Flat.objects.filter(owner=request.user).prefetch_related('flat_account')
    context = {
        "object_list": flats
    }
    return render(request, "cabinet/pages/user_profile_detail.html", context=context)


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


def receipt_pdf_view(request, pk):
    receipt = Receipt.objects.filter(pk=pk) \
        .select_related('account__account_flat__owner') \
        .prefetch_related('bill_receipt') \
        .annotate(total_price=models.Sum('bill_receipt__cost')).order_by('-created').last()
    company_credentials = CompanyCredentials.objects.last()
    context = {
        'request': request,
        "receipt": receipt,
        "company_credentials": company_credentials,
        "tax_size": (receipt.total_price / 5),
        "total_summ": (receipt.total_price * 6 / 5)
    }
    return PdfFactory('cabinet/elements/templates/file.html', context=context, filename='pdf_file').get_response()
