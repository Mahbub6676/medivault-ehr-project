"""Lab test tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Department, Doctor
from patients.models import Patient

from .models import LabTest

User = get_user_model()
PASSWORD = "Medivault@123"


class LabTestTests(TestCase):
    def setUp(self):
        department = Department.objects.create(name="Pathology")
        doctor_user = User.objects.create_user(username="doc_l", password=PASSWORD,
                                               role=User.ROLE_DOCTOR)
        self.doctor = Doctor.objects.create(user=doctor_user, department=department,
                                            specialization="Pathology",
                                            qualification="MBBS", experience=5)
        patient_user = User.objects.create_user(username="pat_l", password=PASSWORD,
                                                role=User.ROLE_PATIENT)
        self.patient = Patient.objects.create(user=patient_user, gender="Female")

    def test_doctor_adds_lab_test(self):
        self.client.login(username="doc_l", password=PASSWORD)
        response = self.client.post(reverse("lab_tests:add"), {
            "patient": self.patient.pk, "doctor": self.doctor.pk,
            "test_name": "CBC", "test_date": "2030-06-01",
            "result": "", "reference_range": "4 - 11", "status": "Pending", "notes": "",
        })
        self.assertEqual(response.status_code, 302)
        test = LabTest.objects.get()
        self.assertTrue(test.test_id.startswith("LAB-"))
        self.assertEqual(test.status, "Pending")

    def test_patient_sees_own_result_only(self):
        mine = LabTest.objects.create(patient=self.patient, doctor=self.doctor,
                                      test_name="CBC", status="Completed", result="Normal")
        other_user = User.objects.create_user(username="pat_l2", password=PASSWORD,
                                              role=User.ROLE_PATIENT)
        other = Patient.objects.create(user=other_user, gender="Male")
        theirs = LabTest.objects.create(patient=other, doctor=self.doctor,
                                        test_name="Lipid Profile", status="Completed")
        self.client.login(username="pat_l", password=PASSWORD)
        response = self.client.get(reverse("lab_tests:list"))
        self.assertContains(response, mine.test_id)
        self.assertNotContains(response, theirs.test_id)
