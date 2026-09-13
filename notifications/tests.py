"""Notification tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Notification, notify

User = get_user_model()
PASSWORD = "Medivault@123"


class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="note_u", password=PASSWORD,
                                             role=User.ROLE_PATIENT)
        self.other = User.objects.create_user(username="note_o", password=PASSWORD,
                                              role=User.ROLE_PATIENT)

    def test_notify_creates_notification(self):
        notify(self.user, "Test title", "Test message", "SYSTEM")
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 1)

    def test_user_sees_only_own_notifications(self):
        notify(self.user, "Mine", "for me")
        notify(self.other, "Theirs", "for them")
        self.client.login(username="note_u", password=PASSWORD)
        response = self.client.get(reverse("notifications:list"))
        self.assertContains(response, "Mine")
        self.assertNotContains(response, "Theirs")

    def test_mark_all_read(self):
        notify(self.user, "One")
        notify(self.user, "Two")
        self.client.login(username="note_u", password=PASSWORD)
        self.client.get(reverse("notifications:mark_all_read"))
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 0)
