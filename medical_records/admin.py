from django.contrib import admin

from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("record_id", "patient", "doctor", "visit_date",
                    "chief_complaint", "follow_up_date")
    list_filter = ("visit_date", "doctor")
    search_fields = ("record_id", "patient__patient_id", "diagnosis", "chief_complaint")
    ordering = ("-visit_date",)
