"""Appointment model with doctor double-booking protection."""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from accounts.utils import next_code
from doctors.models import Doctor
from patients.models import Patient


class Appointment(models.Model):
    STATUS_SCHEDULED = "Scheduled"
    STATUS_CONFIRMED = "Confirmed"
    STATUS_COMPLETED = "Completed"
    STATUS_CANCELLED = "Cancelled"
    STATUS_NO_SHOW = "No Show"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_NO_SHOW, "No Show"),
    ]

    BADGES = {
        STATUS_SCHEDULED: "secondary",
        STATUS_CONFIRMED: "info",
        STATUS_COMPLETED: "success",
        STATUS_CANCELLED: "danger",
        STATUS_NO_SHOW: "warning",
    }

    appointment_id = models.CharField(max_length=20, unique=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-appointment_date", "-appointment_time"]
        # A doctor cannot have two appointments at the same date and time.
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "appointment_date", "appointment_time"],
                name="unique_doctor_slot",
            )
        ]

    def clean(self):
        """Friendly validation message for conflicting slots."""
        conflict = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            appointment_time=self.appointment_time,
        ).exclude(pk=self.pk)
        if self.doctor_id and conflict.exists():
            raise ValidationError(
                "This doctor already has an appointment at the selected date and time."
            )

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            self.appointment_id = next_code(Appointment, "appointment_id", "APT")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.appointment_id} - {self.patient.full_name} with {self.doctor.full_name}"

    @property
    def badge(self):
        return self.BADGES.get(self.status, "secondary")

    def get_absolute_url(self):
        return reverse("appointments:detail", args=[self.pk])
