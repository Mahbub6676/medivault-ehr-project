"""Doctor and department tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Department, Doctor

User = get_user_model()
PASSWORD = "Medivault@123"


class DoctorTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin_d", password=PASSWORD,
                                              role=User.ROLE_ADMIN)
        self.department = Department.objects.create(name="Cardiology")

    def test_doctor_id_generated(self):
        user = User.objects.create_user(username="doc_x", password=PASSWORD,
                                        role=User.ROLE_DOCTOR)
        doctor = Doctor.objects.create(user=user, department=self.department,
                                       specialization="Cardiology",
                                       qualification="MBBS", experience=5)
        self.assertTrue(doctor.doctor_id.startswith("DOC-"))

    def test_admin_can_create_doctor(self):
        self.client.login(username="admin_d", password=PASSWORD)
        response = self.client.post(reverse("doctors:doctor_add"), {
            "first_name": "New", "last_name": "Doctor", "email": "nd@demo.local",
            "phone": "0123", "username": "newdoctor", "password": PASSWORD,
            "department": self.department.pk, "specialization": "Cardiology",
            "qualification": "MBBS", "experience": 3, "consultation_fee": "500.00",
            "available_days": "Mon", "available_time": "09:00 - 12:00", "bio": "Demo",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Doctor.objects.filter(user__username="newdoctor").exists())

    def test_non_admin_cannot_create_doctor(self):
        User.objects.create_user(username="recep_d", password=PASSWORD,
                                 role=User.ROLE_RECEPTIONIST)
        self.client.login(username="recep_d", password=PASSWORD)
        response = self.client.get(reverse("doctors:doctor_add"))
        self.assertEqual(response.status_code, 403)
