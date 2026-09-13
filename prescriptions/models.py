"""Prescription and its medicine lines."""
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.utils import next_code
from doctors.models import Doctor
from medical_records.models import MedicalRecord
from patients.models import Patient


class Prescription(models.Model):
    prescription_id = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, related_name="prescriptions"
    )
    medical_record = models.ForeignKey(
        MedicalRecord, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="prescriptions",
    )
    prescribed_date = models.DateField(default=timezone.now)
    instructions = models.TextField(blank=True, help_text="General advice for the patient")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-prescribed_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.prescription_id:
            self.prescription_id = next_code(Prescription, "prescription_id", "RX")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prescription_id} - {self.patient.full_name}"

    def get_absolute_url(self):
        return reverse("prescriptions:detail", args=[self.pk])


class PrescriptionItem(models.Model):
    """One medicine inside a prescription."""

    ROUTE_CHOICES = [
        ("Oral", "Oral"), ("Topical", "Topical"), ("Injection", "Injection"),
        ("Inhalation", "Inhalation"), ("Drops", "Drops"),
    ]

    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="items"
    )
    medicine_name = models.CharField(max_length=120)
    dosage = models.CharField(max_length=60, help_text="e.g. 500 mg")
    frequency = models.CharField(max_length=60, help_text="e.g. 1+0+1 (twice a day)")
    duration = models.CharField(max_length=60, help_text="e.g. 7 days")
    route = models.CharField(max_length=30, choices=ROUTE_CHOICES, default="Oral")
    special_instruction = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.medicine_name} {self.dosage}"
