"""Authentication and role permission tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()
PASSWORD = "Medivault@123"


class AuthenticationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_t", password=PASSWORD, role=User.ROLE_ADMIN,
            email="admin_t@medivault.local",
        )
        self.patient_user = User.objects.create_user(
            username="patient_t", password=PASSWORD, role=User.ROLE_PATIENT,
        )

    def test_password_is_hashed(self):
        self.assertNotEqual(self.admin.password, PASSWORD)
        self.assertTrue(self.admin.check_password(PASSWORD))

    def test_login_with_username(self):
        response = self.client.post(reverse("accounts:login"),
                                    {"username": "admin_t", "password": PASSWORD})
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_login_with_email(self):
        response = self.client.post(reverse("accounts:login"),
                                    {"username": "admin_t@medivault.local", "password": PASSWORD})
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(reverse("accounts:login"),
                                    {"username": "admin_t", "password": "wrong-password"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_only_admin_can_manage_users(self):
        self.client.login(username="patient_t", password=PASSWORD)
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="admin_t", password=PASSWORD)
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username="admin_t", password=PASSWORD)
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("home"))
