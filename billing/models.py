"""Billing and invoicing model."""

from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.utils import next_code
from appointments.models import Appointment
from patients.models import Patient


class Billing(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_PAID = "Paid"
    STATUS_CANCELLED = "Cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    METHOD_CHOICES = [
        ("Cash", "Cash"), ("Card", "Card"), ("Mobile Banking", "Mobile Banking"),
    ]
    BADGES = {STATUS_PENDING: "warning", STATUS_PAID: "success", STATUS_CANCELLED: "danger"}

    invoice_id = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="bills")
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="bills"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    payment_method = models.CharField(
        max_length=20, choices=METHOD_CHOICES, blank=True
    )
    issued_date = models.DateField(default=timezone.now)
    paid_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_date", "-id"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = next_code(Billing, "invoice_id", "INV")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_id} - {self.patient.full_name}"

    @property
    def badge(self):
        return self.BADGES.get(self.payment_status, "secondary")

    def get_absolute_url(self):
        return reverse("billing:detail", args=[self.pk])
