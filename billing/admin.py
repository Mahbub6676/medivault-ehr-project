from django.contrib import admin

from .models import Billing


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ("invoice_id", "patient", "amount", "payment_status",
                    "payment_method", "issued_date", "paid_date")
    list_filter = ("payment_status", "payment_method", "issued_date")
    search_fields = ("invoice_id", "patient__patient_id", "patient__user__first_name")
    ordering = ("-issued_date",)
