"""Lab test views."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import clinical_required
from notifications.models import notify

from .forms import LabTestForm
from .models import LabTest


def visible_tests(user):
    qs = LabTest.objects.select_related("patient__user", "doctor__user")
    if user.is_superuser or user.is_admin or user.is_receptionist:
        return qs
    if user.is_doctor:
        return qs.filter(doctor__user=user)
    return qs.filter(patient__user=user)


@login_required
def lab_test_list(request):
    qs = visible_tests(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if query:
        qs = qs.filter(
            Q(test_id__icontains=query)
            | Q(test_name__icontains=query)
            | Q(patient__patient_id__icontains=query)
            | Q(patient__user__first_name__icontains=query)
            | Q(patient__user__last_name__icontains=query)
        )
    if status:
        qs = qs.filter(status=status)
    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    return render(request, "lab_tests/lab_test_list.html", {
        "page_obj": page, "query": query, "status": status,
        "statuses": LabTest.STATUS_CHOICES,
    })


@login_required
def lab_test_detail(request, pk):
    test = get_object_or_404(visible_tests(request.user), pk=pk)
    return render(request, "lab_tests/lab_test_detail.html", {"test": test})


@clinical_required
def lab_test_add(request):
    doctor = getattr(request.user, "doctor_profile", None)
    initial = {}
    if request.GET.get("patient"):
        initial["patient"] = request.GET["patient"]
    if request.GET.get("record"):
        initial["medical_record"] = request.GET["record"]
    form = LabTestForm(request.POST or None, doctor=doctor, initial=initial)
    if request.method == "POST" and form.is_valid():
        test = form.save(commit=False)
        if doctor is not None:
            test.doctor = doctor
        test.save()
        notify(
            test.patient.user, "Lab test requested",
            f"{test.test_name} ({test.test_id}) has been requested.", "LAB",
        )
        messages.success(request, f"Lab test {test.test_id} created.")
        return redirect("lab_tests:detail", pk=test.pk)
    return render(request, "lab_tests/lab_test_form.html", {
        "form": form, "title": "Add Lab Test",
    })


@clinical_required
def lab_test_edit(request, pk):
    test = get_object_or_404(LabTest, pk=pk)
    doctor = getattr(request.user, "doctor_profile", None)
    form = LabTestForm(request.POST or None, instance=test, doctor=doctor)
    if request.method == "POST" and form.is_valid():
        test = form.save()
        if test.status == LabTest.STATUS_COMPLETED:
            notify(
                test.patient.user, "Lab result available",
                f"Result for {test.test_name} ({test.test_id}) has been published.", "LAB",
            )
        messages.success(request, "Lab test updated.")
        return redirect("lab_tests:detail", pk=test.pk)
    return render(request, "lab_tests/lab_test_form.html", {
        "form": form, "title": f"Update {test.test_id}",
    })
