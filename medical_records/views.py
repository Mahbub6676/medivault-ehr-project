"""Medical record views (create / edit / view / print)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import clinical_required
from notifications.models import notify

from .forms import MedicalRecordForm
from .models import MedicalRecord


def visible_records(user):
    qs = MedicalRecord.objects.select_related("patient__user", "doctor__user", "appointment")
    if user.is_superuser or user.is_admin or user.is_receptionist:
        return qs
    if user.is_doctor:
        return qs.filter(doctor__user=user)
    return qs.filter(patient__user=user)


@login_required
def record_list(request):
    qs = visible_records(request.user)
    query = request.GET.get("q", "").strip()
    if query:
        qs = qs.filter(
            Q(record_id__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(patient__user__first_name__icontains=query)
            | Q(patient__user__last_name__icontains=query)
            | Q(diagnosis__icontains=query)
        )
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "medical_records/record_list.html", {
        "page_obj": page, "query": query,
    })


@login_required
def record_detail(request, pk):
    record = get_object_or_404(visible_records(request.user), pk=pk)
    return render(request, "medical_records/record_detail.html", {
        "record": record,
        "prescriptions": record.prescriptions.prefetch_related("items"),
        "lab_tests": record.lab_tests.all(),
    })


@login_required
def record_print(request, pk):
    record = get_object_or_404(visible_records(request.user), pk=pk)
    return render(request, "medical_records/record_print.html", {
        "record": record,
        "prescriptions": record.prescriptions.prefetch_related("items"),
        "lab_tests": record.lab_tests.all(),
    })


@clinical_required
def record_add(request):
    doctor = getattr(request.user, "doctor_profile", None)
    initial = {}
    patient_id = request.GET.get("patient")
    appointment_id = request.GET.get("appointment")
    if patient_id:
        initial["patient"] = patient_id
    if appointment_id:
        initial["appointment"] = appointment_id

    form = MedicalRecordForm(request.POST or None, doctor=doctor, initial=initial)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        if doctor is not None:
            record.doctor = doctor
        record.save()
        notify(
            record.patient.user,
            "New medical record",
            f"Dr. {record.doctor.user.full_name if record.doctor else 'Staff'} added record "
            f"{record.record_id} ({record.diagnosis[:60]}).",
            "RECORD",
        )
        messages.success(request, f"Medical record {record.record_id} created.")
        return redirect("medical_records:detail", pk=record.pk)
    return render(request, "medical_records/record_form.html", {
        "form": form, "title": "New Medical Record",
    })


@clinical_required
def record_edit(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    doctor = getattr(request.user, "doctor_profile", None)
    if doctor is not None and record.doctor_id != doctor.pk:
        raise PermissionDenied("You can only edit medical records you created.")
    form = MedicalRecordForm(request.POST or None, instance=record, doctor=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Medical record updated.")
        return redirect("medical_records:detail", pk=record.pk)
    return render(request, "medical_records/record_form.html", {
        "form": form, "title": f"Edit {record.record_id}",
    })
