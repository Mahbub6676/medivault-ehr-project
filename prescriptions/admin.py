from django.contrib import admin

from .models import Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("prescription_id", "patient", "doctor", "prescribed_date")
    list_filter = ("prescribed_date", "doctor")
    search_fields = ("prescription_id", "patient__patient_id", "patient__user__first_name")
    ordering = ("-prescribed_date",)
    inlines = [PrescriptionItemInline]


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ("medicine_name", "dosage", "frequency", "duration", "route", "prescription")
    list_filter = ("route",)
    search_fields = ("medicine_name", "prescription__prescription_id")
    ordering = ("medicine_name",)
