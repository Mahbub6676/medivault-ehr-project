"""Patient creation and patient data isolation tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Patient

User = get_user_model()
PASSWORD = "Medivault@123"


def make_patient(username, first="Test", last="Patient"):
    user = User.objects.create_user(username=username, password=PASSWORD,
                                    first_name=first, last_name=last,
                                    role=User.ROLE_PATIENT)
    return Patient.objects.create(user=user, gender="Male", blood_group="O+")


class PatientModelTests(TestCase):
    def test_patient_id_is_generated(self):
        patient = make_patient("p_model")
        self.assertTrue(patient.patient_id.startswith("PAT-"))


class PatientViewTests(TestCase):
    def setUp(self):
        self.reception = User.objects.create_user(
            username="recep_t", password=PASSWORD, role=User.ROLE_RECEPTIONIST)
        self.patient_a = make_patient("pat_a", "Alice", "A")
        self.patient_b = make_patient("pat_b", "Bob", "B")

    def test_receptionist_can_register_patient(self):
        self.client.login(username="recep_t", password=PASSWORD)
        response = self.client.post(reverse("patients:patient_add"), {
            "first_name": "New", "last_name": "Patient", "email": "new@demo.local",
            "username": "newpatient", "password": PASSWORD,
            "date_of_birth": "1990-01-01", "gender": "Female", "blood_group": "A+",
            "phone": "0123456789", "address": "Demo street",
            "emergency_contact_name": "Family", "emergency_contact_phone": "0987654321",
            "allergies": "None", "chronic_conditions": "None",
        })
        self.assertEqual(Patient.objects.filter(user__username="newpatient").count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_patient_cannot_open_another_patient_record(self):
        self.client.login(username="pat_a", password=PASSWORD)
        response = self.client.get(
            reverse("patients:patient_detail", args=[self.patient_b.pk]))
        self.assertEqual(response.status_code, 403)

    def test_patient_can_open_own_record(self):
        self.client.login(username="pat_a", password=PASSWORD)
        response = self.client.get(
            reverse("patients:patient_detail", args=[self.patient_a.pk]))
        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_list_all_patients(self):
        self.client.login(username="pat_a", password=PASSWORD)
        response = self.client.get(reverse("patients:patient_list"))
        self.assertEqual(response.status_code, 403)

    def test_search_by_patient_id(self):
        self.client.login(username="recep_t", password=PASSWORD)
        response = self.client.get(reverse("patients:patient_list"),
                                   {"q": self.patient_a.patient_id})
        self.assertContains(response, self.patient_a.patient_id)
        self.assertNotContains(response, self.patient_b.patient_id)
