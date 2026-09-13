"""Billing / invoice views."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import front_desk_required
from notifications.models import notify

from .forms import BillingForm
from .models import Billing


def visible_bills(user):
    qs = Billing.objects.select_related("patient__user", "appointment")
    if user.is_superuser or user.is_admin or user.is_receptionist:
        return qs
    if user.is_doctor:
        return qs.filter(appointment__doctor__user=user)
    return qs.filter(patient__user=user)


@login_required
def invoice_list(request):
    qs = visible_bills(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if query:
        qs = qs.filter(
            Q(invoice_id__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(patient__user__first_name__icontains=query)
            | Q(patient__user__last_name__icontains=query)
        )
    if status:
        qs = qs.filter(payment_status=status)

    totals = {
        "total": qs.aggregate(v=Sum("amount"))["v"] or 0,
        "paid": qs.filter(payment_status=Billing.STATUS_PAID)
                  .aggregate(v=Sum("amount"))["v"] or 0,
        "pending": qs.filter(payment_status=Billing.STATUS_PENDING)
                     .aggregate(v=Sum("amount"))["v"] or 0,
    }
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "billing/invoice_list.html", {
        "page_obj": page, "query": query, "status": status,
        "statuses": Billing.STATUS_CHOICES, "totals": totals,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(visible_bills(request.user), pk=pk)
    return render(request, "billing/invoice_detail.html", {"invoice": invoice})


@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(visible_bills(request.user), pk=pk)
    return render(request, "billing/invoice_print.html", {"invoice": invoice})


@front_desk_required
def invoice_add(request):
    initial = {}
    if request.GET.get("patient"):
        initial["patient"] = request.GET["patient"]
    if request.GET.get("appointment"):
        initial["appointment"] = request.GET["appointment"]
    form = BillingForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        invoice = form.save()
        notify(
            invoice.patient.user, "New invoice issued",
            f"Invoice {invoice.invoice_id} of amount {invoice.amount} is "
            f"{invoice.payment_status.lower()}.", "BILLING",
        )
        messages.success(request, f"Invoice {invoice.invoice_id} generated.")
        return redirect("billing:detail", pk=invoice.pk)
    return render(request, "billing/invoice_form.html", {
        "form": form, "title": "Generate Invoice",
    })


@front_desk_required
def invoice_edit(request, pk):
    invoice = get_object_or_404(Billing, pk=pk)
    form = BillingForm(request.POST or None, instance=invoice)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Invoice updated.")
        return redirect("billing:detail", pk=invoice.pk)
    return render(request, "billing/invoice_form.html", {
        "form": form, "title": f"Edit {invoice.invoice_id}",
    })


@front_desk_required
def invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Billing, pk=pk)
    invoice.payment_status = Billing.STATUS_PAID
    invoice.paid_date = timezone.now().date()
    if not invoice.payment_method:
        invoice.payment_method = "Cash"
    invoice.save()
    notify(
        invoice.patient.user, "Payment received",
        f"Invoice {invoice.invoice_id} has been marked as paid. Thank you.", "BILLING",
    )
    messages.success(request, f"Invoice {invoice.invoice_id} marked as paid.")
    return redirect("billing:detail", pk=invoice.pk)
