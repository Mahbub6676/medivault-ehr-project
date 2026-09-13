"""Medical record - the core clinical document of MediVault."""
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.utils import next_code
from appointments.models import Appointment
from doctors.models import Doctor
from patients.models import Patient


class MedicalRecord(models.Model):
    record_id = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medical_records"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, related_name="medical_records"
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="medical_records",
    )
    visit_date = models.DateField(default=timezone.now)
    chief_complaint = models.CharField(max_length=200)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField()
    treatment_plan = models.TextField(blank=True)
    clinical_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-visit_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.record_id:
            self.record_id = next_code(MedicalRecord, "record_id", "MR")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.record_id} - {self.patient.full_name}"

    def get_absolute_url(self):
        return reverse("medical_records:detail", args=[self.pk])
