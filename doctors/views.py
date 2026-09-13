"""Views for department and doctor management."""
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, staff_required

from .forms import DepartmentForm, DoctorForm
from .models import Department, Doctor


# ----------------------------- Departments --------------------------------
@staff_required
def department_list(request):
    query = request.GET.get("q", "").strip()
    departments = Department.objects.annotate(doctor_count=Count("doctors")).order_by("name")
    if query:
        departments = departments.filter(name__icontains=query)
    page = Paginator(departments, 10).get_page(request.GET.get("page"))
    return render(request, "doctors/department_list.html", {
        "page_obj": page, "query": query, "form": DepartmentForm(),
    })


@admin_required
def department_add(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department created.")
        return redirect("doctors:department_list")
    return render(request, "doctors/department_form.html", {
        "form": form, "title": "Add Department",
    })


@admin_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Department updated.")
        return redirect("doctors:department_list")
    return render(request, "doctors/department_form.html", {
        "form": form, "title": f"Edit Department - {department.name}",
    })


# ------------------------------- Doctors -----------------------------------
@staff_required
def doctor_list(request):
    query = request.GET.get("q", "").strip()
    department = request.GET.get("department", "")
    doctors = Doctor.objects.select_related("user", "department")
    if query:
        doctors = doctors.filter(
            Q(doctor_id__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(specialization__icontains=query)
            | Q(department__name__icontains=query)
        )
    if department:
        doctors = doctors.filter(department_id=department)
    page = Paginator(doctors, 10).get_page(request.GET.get("page"))
    return render(request, "doctors/doctor_list.html", {
        "page_obj": page, "query": query, "department": department,
        "departments": Department.objects.all(),
    })


@staff_required
def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related("user", "department"), pk=pk
    )
    appointments = doctor.appointments.select_related("patient__user")[:10]
    return render(request, "doctors/doctor_detail.html", {
        "doctor": doctor, "appointments": appointments,
        "total_appointments": doctor.appointments.count(),
        "total_records": doctor.medical_records.count(),
    })


@admin_required
def doctor_add(request):
    form = DoctorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save()
        messages.success(request, f"Doctor {doctor.doctor_id} created successfully.")
        return redirect("doctors:doctor_detail", pk=doctor.pk)
    return render(request, "doctors/doctor_form.html", {"form": form, "title": "Add Doctor"})


@admin_required
def doctor_edit(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    form = DoctorForm(request.POST or None, instance=doctor)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Doctor profile updated.")
        return redirect("doctors:doctor_detail", pk=doctor.pk)
    return render(request, "doctors/doctor_form.html", {
        "form": form, "title": f"Edit Doctor - {doctor.doctor_id}", "doctor": doctor,
    })


@admin_required
def doctor_toggle_active(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    doctor.user.is_active = not doctor.user.is_active
    doctor.user.save(update_fields=["is_active"])
    state = "activated" if doctor.user.is_active else "deactivated"
    messages.success(request, f"Doctor {doctor.doctor_id} {state}.")
    return redirect("doctors:doctor_detail", pk=doctor.pk)
