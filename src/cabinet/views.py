from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
# (login_url='account_login')
from django.urls import reverse
from django.views.generic import DetailView

from src.admin_panel.forms import ReceiptCreateForm
from src.admin_panel.models import Flat, Receipt, Account, Bill
from src.cabinet.services.export_to_excel import WriteToExcel
from src.cabinet.services.export_to_pdf import WriteToPdf


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

