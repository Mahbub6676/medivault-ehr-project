"""Dashboard tests for Admin, Doctor, Receptionist, and Patient roles."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Department, Doctor
from patients.models import Patient

User = get_user_model()
PASSWORD = "Medivault@123"


class DashboardViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_dash", password=PASSWORD, role=User.ROLE_ADMIN, is_superuser=True
        )
        self.doc_user = User.objects.create_user(
            username="doctor_dash", password=PASSWORD, role=User.ROLE_DOCTOR
        )
        self.dept = Department.objects.create(name="Cardiology", description="Heart care")
        self.doctor = Doctor.objects.create(
            user=self.doc_user, department=self.dept, specialization="Cardiology"
        )
        self.rec_user = User.objects.create_user(
            username="recep_dash", password=PASSWORD, role=User.ROLE_RECEPTIONIST
        )
        self.pat_user = User.objects.create_user(
            username="patient_dash", password=PASSWORD, role=User.ROLE_PATIENT
        )
        self.patient = Patient.objects.create(
            user=self.pat_user, gender="Female", blood_group="A+"
        )

    def test_unauthenticated_user_redirected(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_admin_dashboard(self):
        self.client.login(username="admin_dash", password=PASSWORD)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/admin_dashboard.html")

    def test_doctor_dashboard(self):
        self.client.login(username="doctor_dash", password=PASSWORD)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/doctor_dashboard.html")

    def test_receptionist_dashboard(self):
        self.client.login(username="recep_dash", password=PASSWORD)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/receptionist_dashboard.html")

    def test_patient_dashboard(self):
        self.client.login(username="patient_dash", password=PASSWORD)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard/patient_dashboard.html")
