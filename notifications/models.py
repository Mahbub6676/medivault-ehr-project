"""In-app notification model plus a tiny helper used by the other apps."""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ("APPOINTMENT", "Appointment"),
        ("PRESCRIPTION", "Prescription"),
        ("LAB", "Lab Test"),
        ("BILLING", "Billing"),
        ("RECORD", "Medical Record"),
        ("SYSTEM", "System"),
    ]

    ICONS = {
        "APPOINTMENT": "bi-calendar-check",
        "PRESCRIPTION": "bi-capsule",
        "LAB": "bi-clipboard2-pulse",
        "BILLING": "bi-receipt",
        "RECORD": "bi-journal-medical",
        "SYSTEM": "bi-bell",
    }

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=150)
    message = models.TextField(blank=True)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="SYSTEM")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.user.username}"

    @property
    def icon(self):
        return self.ICONS.get(self.notification_type, "bi-bell")


def notify(user, title, message="", notification_type="SYSTEM"):
    """Create a notification (safely ignores missing users)."""
    if not user:
        return None
    return Notification.objects.create(
        user=user, title=title, message=message, notification_type=notification_type
    )
