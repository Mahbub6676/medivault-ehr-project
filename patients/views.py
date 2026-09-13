"""Patient management views with strict object level access checks."""
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import front_desk_required, staff_required
from django.contrib.auth.decorators import login_required

from .forms import PatientForm
from .models import Patient


def can_view_patient(user, patient):
    """A patient may only ever open their own record."""
    if user.is_superuser or user.is_staff_member:
        return True
    return user.is_patient and patient.user_id == user.id


@staff_required
def patient_list(request):
    query = request.GET.get("q", "").strip()
    gender = request.GET.get("gender", "")
    status = request.GET.get("status", "")
    patients = Patient.objects.select_related("user")

    if query:
        patients = patients.filter(
            Q(patient_id__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(phone__icontains=query)
        )
    if gender:
        patients = patients.filter(gender=gender)
    if status == "active":
        patients = patients.filter(user__is_active=True)
    elif status == "inactive":
        patients = patients.filter(user__is_active=False)

    page = Paginator(patients, 10).get_page(request.GET.get("page"))
    return render(request, "patients/patient_list.html", {
        "page_obj": page, "query": query, "gender": gender, "status": status,
        "genders": Patient.GENDER_CHOICES,
    })


@front_desk_required
def patient_add(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save()
        messages.success(request, f"Patient {patient.patient_id} registered successfully.")
        return redirect("patients:patient_detail", pk=patient.pk)
    return render(request, "patients/patient_form.html", {
        "form": form, "title": "Register New Patient",
    })


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
    if not can_view_patient(request.user, patient):
        raise PermissionDenied("You may only view your own medical information.")

    context = {
        "patient": patient,
        "appointments": patient.appointments.select_related("doctor__user")[:10],
        "records": patient.medical_records.select_related("doctor__user")[:10],
        "prescriptions": patient.prescriptions.select_related("doctor__user")[:10],
        "lab_tests": patient.lab_tests.select_related("doctor__user")[:10],
        "bills": patient.bills.all()[:10],
    }
    return render(request, "patients/patient_detail.html", context)


@front_desk_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Patient details updated.")
        return redirect("patients:patient_detail", pk=patient.pk)
    return render(request, "patients/patient_form.html", {
        "form": form, "title": f"Edit Patient - {patient.patient_id}", "patient": patient,
    })


@front_desk_required
def patient_toggle_active(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.user.is_active = not patient.user.is_active
    patient.user.save(update_fields=["is_active"])
    state = "activated" if patient.user.is_active else "deactivated"
    messages.success(request, f"Patient {patient.patient_id} {state}.")
    return redirect("patients:patient_detail", pk=patient.pk)


@login_required
def patient_print(request, pk):
    """Print friendly patient summary sheet."""
    patient = get_object_or_404(Patient.objects.select_related("user"), pk=pk)
    if not can_view_patient(request.user, patient):
        raise PermissionDenied("You may only print your own patient summary.")
    return render(request, "patients/patient_print.html", {
        "patient": patient,
        "records": patient.medical_records.select_related("doctor__user")[:10],
        "appointments": patient.appointments.select_related("doctor__user")[:10],
    })


@login_required
def my_profile(request):
    """Shortcut used by the patient sidebar."""
    if not request.user.is_patient:
        return redirect("dashboard:home")
    patient = get_object_or_404(Patient, user=request.user)
    return redirect("patients:patient_detail", pk=patient.pk)
