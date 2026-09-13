from django.contrib import admin

from .models import LabTest


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ("test_id", "test_name", "patient", "doctor", "test_date", "status")
    list_filter = ("status", "test_date")
    search_fields = ("test_id", "test_name", "patient__patient_id")
    ordering = ("-test_date",)
