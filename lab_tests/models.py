"""Laboratory test requests and results."""
from django.db import models
from django.urls import reverse
from django.utils import timezone

from accounts.utils import next_code
from doctors.models import Doctor
from medical_records.models import MedicalRecord
from patients.models import Patient


class LabTest(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_COMPLETED = "Completed"
    STATUS_CHOICES = [(STATUS_PENDING, "Pending"), (STATUS_COMPLETED, "Completed")]

    test_id = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="lab_tests")
    doctor = models.ForeignKey(
        Doctor, on_delete=models.SET_NULL, null=True, related_name="lab_tests"
    )
    medical_record = models.ForeignKey(
        MedicalRecord, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lab_tests",
    )
    test_name = models.CharField(max_length=120)
    test_date = models.DateField(default=timezone.now)
    result = models.TextField(blank=True)
    reference_range = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-test_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.test_id:
            self.test_id = next_code(LabTest, "test_id", "LAB")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.test_id} - {self.test_name}"

    @property
    def badge(self):
        return "success" if self.status == self.STATUS_COMPLETED else "warning"

    def get_absolute_url(self):
        return reverse("lab_tests:detail", args=[self.pk])
