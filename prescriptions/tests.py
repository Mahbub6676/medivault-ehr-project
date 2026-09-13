"""Prescription tests (multiple medicines per prescription)."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Department, Doctor
from patients.models import Patient

from .models import Prescription

User = get_user_model()
PASSWORD = "Medivault@123"


class PrescriptionTests(TestCase):
    def setUp(self):
        department = Department.objects.create(name="General Medicine")
        doctor_user = User.objects.create_user(username="doc_p", password=PASSWORD,
                                               role=User.ROLE_DOCTOR)
        self.doctor = Doctor.objects.create(user=doctor_user, department=department,
                                            specialization="Medicine",
                                            qualification="MBBS", experience=3)
        patient_user = User.objects.create_user(username="pat_p", password=PASSWORD,
                                                role=User.ROLE_PATIENT)
        self.patient = Patient.objects.create(user=patient_user, gender="Male")

    def test_doctor_creates_prescription_with_two_medicines(self):
        self.client.login(username="doc_p", password=PASSWORD)
        data = {
            "patient": self.patient.pk, "doctor": self.doctor.pk,
            "prescribed_date": "2030-05-01",
            "instructions": "Take after meals", "notes": "",
            "items-TOTAL_FORMS": "2", "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "0", "items-MAX_NUM_FORMS": "1000",
            "items-0-medicine_name": "Amoxicillin", "items-0-dosage": "500 mg",
            "items-0-frequency": "1+0+1", "items-0-duration": "7 days",
            "items-0-route": "Oral", "items-0-special_instruction": "After meal",
            "items-1-medicine_name": "Paracetamol", "items-1-dosage": "500 mg",
            "items-1-frequency": "1+1+1", "items-1-duration": "5 days",
            "items-1-route": "Oral", "items-1-special_instruction": "",
        }
        response = self.client.post(reverse("prescriptions:add"), data)
        self.assertEqual(response.status_code, 302)
        prescription = Prescription.objects.get()
        self.assertTrue(prescription.prescription_id.startswith("RX-"))
        self.assertEqual(prescription.items.count(), 2)

    def test_patient_cannot_create_prescription(self):
        self.client.login(username="pat_p", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("prescriptions:add")).status_code, 403)
