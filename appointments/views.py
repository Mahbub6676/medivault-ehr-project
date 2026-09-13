"""Appointment scheduling views."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import front_desk_required, staff_required
from doctors.models import Doctor
from notifications.models import notify
from patients.models import Patient

from .forms import AppointmentForm, PatientAppointmentRequestForm
from .models import Appointment



def visible_appointments(user):
    """Return only the appointments the current user is allowed to see."""
    qs = Appointment.objects.select_related("patient__user", "doctor__user")
    if user.is_superuser or user.is_admin or user.is_receptionist:
        return qs
    if user.is_doctor:
        return qs.filter(doctor__user=user)
    return qs.filter(patient__user=user)


@login_required
def appointment_list(request):
    qs = visible_appointments(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    date = request.GET.get("date", "")
    doctor = request.GET.get("doctor", "")

    if query:
        qs = qs.filter(
            Q(appointment_id__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(patient__user__first_name__icontains=query)
            | Q(patient__user__last_name__icontains=query)
            | Q(doctor__user__last_name__icontains=query)
            | Q(reason__icontains=query)
        )
    if status:
        qs = qs.filter(status=status)
    if date:
        qs = qs.filter(appointment_date=date)
    if doctor:
        qs = qs.filter(doctor_id=doctor)

    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "appointments/appointment_list.html", {
        "page_obj": page, "query": query, "status": status, "date": date,
        "doctor": doctor, "statuses": Appointment.STATUS_CHOICES,
        "doctors": Doctor.objects.select_related("user"),
    })


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related("patient__user", "doctor__user"), pk=pk
    )
    if not visible_appointments(request.user).filter(pk=pk).exists():
        raise PermissionDenied("You cannot view this appointment.")
    return render(request, "appointments/appointment_detail.html", {
        "appointment": appointment,
        "records": appointment.medical_records.all(),
        "bills": appointment.bills.all(),
    })


@front_desk_required
def appointment_add(request):
    form = AppointmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        appointment = form.save()
        notify(
            appointment.patient.user,
            "Appointment scheduled",
            f"Your appointment {appointment.appointment_id} with {appointment.doctor.full_name} "
            f"is on {appointment.appointment_date} at {appointment.appointment_time}.",
            "APPOINTMENT",
        )
        notify(
            appointment.doctor.user,
            "New appointment",
            f"{appointment.patient.full_name} booked {appointment.appointment_date} "
            f"at {appointment.appointment_time}.",
            "APPOINTMENT",
        )
        messages.success(request, f"Appointment {appointment.appointment_id} created.")
        return redirect("appointments:detail", pk=appointment.pk)
    return render(request, "appointments/appointment_form.html", {
        "form": form, "title": "New Appointment",
    })


@staff_required
def appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Appointment updated.")
        return redirect("appointments:detail", pk=appointment.pk)
    return render(request, "appointments/appointment_form.html", {
        "form": form, "title": f"Edit {appointment.appointment_id}",
    })


@staff_required
def appointment_set_status(request, pk, status):
    """Confirm / complete / cancel an appointment in one small view."""
    appointment = get_object_or_404(Appointment, pk=pk)
    valid = dict(Appointment.STATUS_CHOICES)
    status = status.replace("-", " ").title()
    if status not in valid:
        messages.error(request, "Unknown appointment status.")
        return redirect("appointments:detail", pk=pk)

    appointment.status = status
    appointment.save(update_fields=["status"])
    notify(
        appointment.patient.user,
        f"Appointment {status.lower()}",
        f"Appointment {appointment.appointment_id} is now {status}.",
        "APPOINTMENT",
    )
    messages.success(request, f"Appointment marked as {status}.")
    return redirect("appointments:detail", pk=pk)


@login_required
def patient_appointment_request(request):
    if not request.user.is_patient:
        return redirect("appointments:add")
    patient = get_object_or_404(Patient, user=request.user)
    form = PatientAppointmentRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = patient
        appointment.status = Appointment.STATUS_SCHEDULED
        appointment.save()
        notify(
            appointment.doctor.user,
            "New Patient Appointment Request",
            f"Patient {patient.full_name} requested an appointment on {appointment.appointment_date} at {appointment.appointment_time}.",
            "APPOINTMENT",
        )
        messages.success(
            request,
            f"Appointment request {appointment.appointment_id} submitted successfully.",
        )
        return redirect("appointments:detail", pk=appointment.pk)
    return render(request, "appointments/appointment_request.html", {
        "form": form, "title": "Book an Appointment",
    })

