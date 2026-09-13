"""Prescription views - supports several medicines per prescription."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render


from accounts.decorators import clinical_required
from notifications.models import notify

from .forms import PrescriptionForm, PrescriptionItemFormSet
from .models import Prescription


def visible_prescriptions(user):
    qs = Prescription.objects.select_related("patient__user", "doctor__user").prefetch_related(
        "items"
    )
    if user.is_superuser or user.is_admin or user.is_receptionist:
        return qs
    if user.is_doctor:
        return qs.filter(doctor__user=user)
    return qs.filter(patient__user=user)


@login_required
def prescription_list(request):
    qs = visible_prescriptions(request.user)
    query = request.GET.get("q", "").strip()
    if query:
        qs = qs.filter(
            Q(prescription_id__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(patient__user__first_name__icontains=query)
            | Q(patient__user__last_name__icontains=query)
            | Q(items__medicine_name__icontains=query)
        ).distinct()
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "prescriptions/prescription_list.html", {
        "page_obj": page, "query": query,
    })


@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(visible_prescriptions(request.user), pk=pk)
    return render(request, "prescriptions/prescription_detail.html",
                  {"prescription": prescription})


@login_required
def prescription_print(request, pk):
    prescription = get_object_or_404(visible_prescriptions(request.user), pk=pk)
    return render(request, "prescriptions/prescription_print.html",
                  {"prescription": prescription})


@clinical_required
def prescription_add(request):
    doctor = getattr(request.user, "doctor_profile", None)
    initial = {}
    if request.GET.get("patient"):
        initial["patient"] = request.GET["patient"]
    if request.GET.get("record"):
        initial["medical_record"] = request.GET["record"]

    form = PrescriptionForm(request.POST or None, doctor=doctor, initial=initial)
    formset = PrescriptionItemFormSet(request.POST or None)

    if request.method == "POST" and form.is_valid() and formset.is_valid():
        prescription = form.save(commit=False)
        if doctor is not None:
            prescription.doctor = doctor
        prescription.save()
        formset.instance = prescription
        formset.save()
        notify(
            prescription.patient.user,
            "New prescription issued",
            f"Prescription {prescription.prescription_id} with "
            f"{prescription.items.count()} medicine(s) is available.",
            "PRESCRIPTION",
        )
        messages.success(request, f"Prescription {prescription.prescription_id} created.")
        return redirect("prescriptions:detail", pk=prescription.pk)

    return render(request, "prescriptions/prescription_form.html", {
        "form": form, "formset": formset, "title": "New Prescription",
    })


@clinical_required
def prescription_edit(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    doctor = getattr(request.user, "doctor_profile", None)
    if doctor is not None and prescription.doctor_id != doctor.pk:
        raise PermissionDenied("You can only edit prescriptions you created.")
    form = PrescriptionForm(request.POST or None, instance=prescription, doctor=doctor)

    formset = PrescriptionItemFormSet(request.POST or None, instance=prescription)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "Prescription updated.")
        return redirect("prescriptions:detail", pk=prescription.pk)
    return render(request, "prescriptions/prescription_form.html", {
        "form": form, "formset": formset, "title": f"Edit {prescription.prescription_id}",
    })
