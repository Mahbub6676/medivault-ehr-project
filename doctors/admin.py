from django.contrib import admin

from .models import Department, Doctor


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("doctor_id", "full_name", "department", "specialization",
                    "experience", "consultation_fee")
    list_filter = ("department", "specialization")
    search_fields = ("doctor_id", "user__first_name", "user__last_name", "specialization")
    ordering = ("doctor_id",)
