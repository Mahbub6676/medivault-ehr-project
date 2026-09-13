"""User model for MediVault EHR.

We extend Django's AbstractUser so that password hashing, sessions and the
admin site keep working exactly as Django intends. A single ``role`` field
drives the role based access control of the whole application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user with a role."""

    ROLE_ADMIN = "ADMIN"
    ROLE_DOCTOR = "DOCTOR"
    ROLE_RECEPTIONIST = "RECEPTIONIST"
    ROLE_PATIENT = "PATIENT"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Administrator"),
        (ROLE_DOCTOR, "Doctor"),
        (ROLE_RECEPTIONIST, "Receptionist"),
        (ROLE_PATIENT, "Patient"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["first_name", "last_name", "username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ---- convenience helpers used inside templates and views -------------
    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_doctor(self):
        return self.role == self.ROLE_DOCTOR

    @property
    def is_receptionist(self):
        return self.role == self.ROLE_RECEPTIONIST

    @property
    def is_patient(self):
        return self.role == self.ROLE_PATIENT

    @property
    def is_staff_member(self):
        """Anyone who is not a patient (admin, doctor, receptionist)."""
        return self.role in (self.ROLE_ADMIN, self.ROLE_DOCTOR, self.ROLE_RECEPTIONIST)

    @property
    def initials(self):
        first = (self.first_name or self.username)[:1]
        last = (self.last_name or "")[:1]
        return (first + last).upper()


class AuditLog(models.Model):
    """HIPAA compliant audit trail for recording access & security events."""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=200, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {username} - {self.action} ({self.resource})"


def log_action(user, action, resource="", details="", ip_address=""):
    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        resource=resource,
        details=details,
        ip_address=ip_address or "",
    )

