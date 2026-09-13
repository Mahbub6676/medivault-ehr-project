"""Patient model."""
from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse

from accounts.utils import next_code


class Patient(models.Model):
    """Patient demographic and basic medical profile."""

    GENDER_CHOICES = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    BLOOD_GROUPS = [(b, b) for b in
                    ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_profile"
    )
    patient_id = models.CharField(max_length=20, unique=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUPS, default="Unknown")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    allergies = models.TextField(blank=True, help_text="Known allergies, comma separated")
    chronic_conditions = models.TextField(blank=True, help_text="e.g. Diabetes, Hypertension")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = next_code(Patient, "patient_id", "PAT")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name} ({self.patient_id})"

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def age(self):
        if not self.date_of_birth:
            return "-"
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def is_active(self):
        return self.user.is_active

    def get_absolute_url(self):
        return reverse("patients:patient_detail", args=[self.pk])
