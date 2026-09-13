"""Role based dashboards with Chart.js statistics."""
import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from appointments.models import Appointment
from billing.models import Billing
from doctors.models import Department, Doctor
from lab_tests.models import LabTest
from medical_records.models import MedicalRecord
from patients.models import Patient
from prescriptions.models import Prescription


@login_required
def dashboard_home(request):
    """Send every user to the dashboard matching their role."""
    user = request.user
    if user.is_superuser or user.is_admin:
        return admin_dashboard(request)
    if user.is_doctor:
        return doctor_dashboard(request)
    if user.is_receptionist:
        return receptionist_dashboard(request)
    if user.is_patient:
        return patient_dashboard(request)
    return redirect("home")


# ------------------------------------------------------------------ ADMIN --
def admin_dashboard(request):
    today = timezone.localdate()

    # Monthly patient registrations for the last 6 months
    labels, monthly = [], []
    cursor = today.replace(day=1)
    months = []
    for _ in range(6):
        months.append(cursor)
        cursor = (cursor - timedelta(days=1)).replace(day=1)
    for month_start in reversed(months):
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        labels.append(month_start.strftime("%b %Y"))
        monthly.append(
            Patient.objects.filter(
                created_at__date__gte=month_start, created_at__date__lt=next_month
            ).count()
        )

    status_rows = Appointment.objects.values("status").annotate(total=Count("id"))
    dept_rows = (
        Appointment.objects.values("doctor__department__name")
        .annotate(total=Count("patient", distinct=True))
        .order_by("-total")[:6]
    )

    context = {
        "total_patients": Patient.objects.count(),
        "total_doctors": Doctor.objects.count(),
        "total_appointments": Appointment.objects.count(),
        "today_appointments": Appointment.objects.filter(appointment_date=today).count(),
        "completed_appointments": Appointment.objects.filter(status="Completed").count(),
        "pending_bills": Billing.objects.filter(payment_status="Pending").count(),
        "pending_amount": Billing.objects.filter(payment_status="Pending")
                                         .aggregate(v=Sum("amount"))["v"] or 0,
        "total_departments": Department.objects.count(),
        "total_records": MedicalRecord.objects.count(),
        "recent_appointments": Appointment.objects.select_related(
            "patient__user", "doctor__user")[:8],
        "recent_patients": Patient.objects.select_related("user")[:5],
        "chart_months": json.dumps(labels),
        "chart_monthly_patients": json.dumps(monthly),
        "chart_status_labels": json.dumps([r["status"] for r in status_rows]),
        "chart_status_values": json.dumps([r["total"] for r in status_rows]),
        "chart_dept_labels": json.dumps(
            [r["doctor__department__name"] or "Unassigned" for r in dept_rows]),
        "chart_dept_values": json.dumps([r["total"] for r in dept_rows]),
    }
    return render(request, "dashboard/admin_dashboard.html", context)


# ----------------------------------------------------------------- DOCTOR --
def doctor_dashboard(request):
    today = timezone.localdate()
    doctor = getattr(request.user, "doctor_profile", None)
    if doctor is None:
        return render(request, "dashboard/no_profile.html", {"role": "doctor"})

    appointments = doctor.appointments.select_related("patient__user")
    context = {
        "doctor": doctor,
        "today_appointments": appointments.filter(appointment_date=today),
        "today_count": appointments.filter(appointment_date=today).count(),
        "total_patients": appointments.values("patient").distinct().count(),
        "completed_visits": appointments.filter(status="Completed").count(),
        "pending_appointments": appointments.filter(
            status__in=["Scheduled", "Confirmed"]).count(),
        "upcoming": appointments.filter(appointment_date__gte=today).order_by(
            "appointment_date", "appointment_time")[:8],
        "recent_records": doctor.medical_records.select_related("patient__user")[:6],
        "pending_labs": doctor.lab_tests.filter(status="Pending")
                                        .select_related("patient__user")[:6],
    }
    return render(request, "dashboard/doctor_dashboard.html", context)


# ----------------------------------------------------------- RECEPTIONIST --
def receptionist_dashboard(request):
    today = timezone.localdate()
    context = {
        "total_patients": Patient.objects.count(),
        "today_appointments": Appointment.objects.filter(appointment_date=today).count(),
        "pending_appointments": Appointment.objects.filter(
            status__in=["Scheduled", "Confirmed"]).count(),
        "today_new_patients": Patient.objects.filter(created_at__date=today).count(),
        "pending_bills": Billing.objects.filter(payment_status="Pending").count(),
        "today_list": Appointment.objects.filter(appointment_date=today).select_related(
            "patient__user", "doctor__user"),
        "recent_patients": Patient.objects.select_related("user")[:6],
        "unpaid_invoices": Billing.objects.filter(payment_status="Pending")
                                          .select_related("patient__user")[:6],
    }
    return render(request, "dashboard/receptionist_dashboard.html", context)


# ---------------------------------------------------------------- PATIENT --
def patient_dashboard(request):
    today = timezone.localdate()
    patient = getattr(request.user, "patient_profile", None)
    if patient is None:
        return render(request, "dashboard/no_profile.html", {"role": "patient"})

    appointments = patient.appointments.select_related("doctor__user")
    last_record = patient.medical_records.select_related("doctor__user").first()
    context = {
        "patient": patient,
        "upcoming_appointment": appointments.filter(
            appointment_date__gte=today).order_by("appointment_date", "appointment_time").first(),
        "total_visits": patient.medical_records.count(),
        "last_record": last_record,
        "recent_diagnosis": last_record.diagnosis if last_record else "No diagnosis yet",
        "active_prescriptions": patient.prescriptions.count(),
        "pending_bills": patient.bills.filter(payment_status="Pending").count(),
        "pending_amount": patient.bills.filter(payment_status="Pending")
                                       .aggregate(v=Sum("amount"))["v"] or 0,
        "appointments": appointments[:5],
        "prescriptions": Prescription.objects.filter(patient=patient)[:5],
        "lab_tests": LabTest.objects.filter(patient=patient)[:5],
        "records": patient.medical_records.select_related("doctor__user")[:5],
    }
    return render(request, "dashboard/patient_dashboard.html", context)
