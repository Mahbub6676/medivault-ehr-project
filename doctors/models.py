"""Department and Doctor models."""
from django.conf import settings
from django.db import models
from django.urls import reverse

from accounts.utils import next_code


class Department(models.Model):
    """A hospital department, e.g. Cardiology."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("doctors:department_list")


class Doctor(models.Model):
    """Doctor profile linked one-to-one with a user account."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor_profile"
    )
    doctor_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors"
    )
    specialization = models.CharField(max_length=120)
    qualification = models.CharField(max_length=120, help_text="e.g. MBBS, FCPS (Cardiology)")
    experience = models.PositiveIntegerField(default=0, help_text="Years of experience")
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    available_days = models.CharField(
        max_length=120, blank=True, help_text="e.g. Monday, Wednesday, Friday"
    )
    available_time = models.CharField(max_length=120, blank=True, help_text="e.g. 09:00 - 14:00")
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["doctor_id"]

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = next_code(Doctor, "doctor_id", "DOC")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.user.full_name} ({self.doctor_id})"

    @property
    def full_name(self):
        return f"Dr. {self.user.full_name}"

    @property
    def is_active(self):
        return self.user.is_active

    def get_absolute_url(self):
        return reverse("doctors:doctor_detail", args=[self.pk])
