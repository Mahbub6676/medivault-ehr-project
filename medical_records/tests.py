"""Medical record creation and access tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Department, Doctor
from patients.models import Patient

from .models import MedicalRecord

User = get_user_model()
PASSWORD = "Medivault@123"


class MedicalRecordTests(TestCase):
    def setUp(self):
        department = Department.objects.create(name="Cardiology")
        doctor_user = User.objects.create_user(username="doc_m", password=PASSWORD,
                                               role=User.ROLE_DOCTOR)
        self.doctor = Doctor.objects.create(user=doctor_user, department=department,
                                            specialization="Cardiology",
                                            qualification="MBBS", experience=7)
        patient_user = User.objects.create_user(username="pat_m", password=PASSWORD,
                                                role=User.ROLE_PATIENT)
        self.patient = Patient.objects.create(user=patient_user, gender="Female")

    def test_doctor_creates_record(self):
        self.client.login(username="doc_m", password=PASSWORD)
        response = self.client.post(reverse("medical_records:add"), {
            "patient": self.patient.pk, "doctor": self.doctor.pk,
            "visit_date": "2030-04-01", "chief_complaint": "Chest pain",
            "symptoms": "Tightness", "diagnosis": "Angina",
            "treatment_plan": "Medication", "clinical_notes": "Stable",
            "follow_up_date": "2030-04-20",
        })
        self.assertEqual(response.status_code, 302)
        record = MedicalRecord.objects.get()
        self.assertTrue(record.record_id.startswith("MR-"))
        self.assertEqual(record.doctor, self.doctor)

    def test_patient_cannot_create_record(self):
        self.client.login(username="pat_m", password=PASSWORD)
        response = self.client.get(reverse("medical_records:add"))
        self.assertEqual(response.status_code, 403)

    def test_patient_sees_only_own_records(self):
        mine = MedicalRecord.objects.create(
            patient=self.patient, doctor=self.doctor, visit_date="2030-01-01",
            chief_complaint="Cough", diagnosis="Bronchitis")
        other_user = User.objects.create_user(username="pat_m2", password=PASSWORD,
                                              role=User.ROLE_PATIENT)
        other = Patient.objects.create(user=other_user, gender="Male")
        theirs = MedicalRecord.objects.create(
            patient=other, doctor=self.doctor, visit_date="2030-01-02",
            chief_complaint="Fever", diagnosis="Flu")

        self.client.login(username="pat_m", password=PASSWORD)
        response = self.client.get(reverse("medical_records:list"))
        self.assertContains(response, mine.record_id)
        self.assertNotContains(response, theirs.record_id)
        self.assertEqual(
            self.client.get(reverse("medical_records:detail", args=[theirs.pk])).status_code,
            404,
        )
