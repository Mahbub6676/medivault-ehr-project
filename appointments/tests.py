"""Appointment creation and conflict tests."""
from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from doctors.models import Department, Doctor
from patients.models import Patient

from .forms import AppointmentForm
from .models import Appointment

User = get_user_model()
PASSWORD = "Medivault@123"


class AppointmentTests(TestCase):
    def setUp(self):
        self.reception = User.objects.create_user(username="recep_a", password=PASSWORD,
                                                  role=User.ROLE_RECEPTIONIST)
        department = Department.objects.create(name="General Medicine")
        doctor_user = User.objects.create_user(username="doc_a", password=PASSWORD,
                                               role=User.ROLE_DOCTOR)
        self.doctor = Doctor.objects.create(user=doctor_user, department=department,
                                            specialization="Internal Medicine",
                                            qualification="MBBS", experience=4)
        patient_user = User.objects.create_user(username="pat_ap", password=PASSWORD,
                                                role=User.ROLE_PATIENT)
        self.patient = Patient.objects.create(user=patient_user, gender="Male")

    def _payload(self):
        return {
            "patient": self.patient.pk, "doctor": self.doctor.pk,
            "appointment_date": "2030-01-15", "appointment_time": "10:00",
            "reason": "Routine checkup", "status": "Scheduled", "notes": "",
        }

    def test_receptionist_creates_appointment(self):
        self.client.login(username="recep_a", password=PASSWORD)
        response = self.client.post(reverse("appointments:add"), self._payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertTrue(Appointment.objects.first().appointment_id.startswith("APT-"))

    def test_duplicate_slot_is_rejected(self):
        Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            appointment_date=date(2030, 1, 15), appointment_time=time(10, 0),
            reason="First visit",
        )
        form = AppointmentForm(data=self._payload())
        self.assertFalse(form.is_valid())
        self.assertIn("Conflict", str(form.errors))

    def test_patient_only_sees_own_appointments(self):
        other_user = User.objects.create_user(username="pat_other", password=PASSWORD,
                                              role=User.ROLE_PATIENT)
        other_patient = Patient.objects.create(user=other_user, gender="Female")
        mine = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor, appointment_date=date(2030, 2, 1),
            appointment_time=time(9, 0), reason="Mine")
        theirs = Appointment.objects.create(
            patient=other_patient, doctor=self.doctor, appointment_date=date(2030, 2, 1),
            appointment_time=time(11, 0), reason="Theirs")

        self.client.login(username="pat_ap", password=PASSWORD)
        response = self.client.get(reverse("appointments:list"))
        self.assertContains(response, mine.appointment_id)
        self.assertNotContains(response, theirs.appointment_id)

    def test_patient_cannot_open_other_appointment(self):
        other_user = User.objects.create_user(username="pat_o2", password=PASSWORD,
                                              role=User.ROLE_PATIENT)
        other_patient = Patient.objects.create(user=other_user, gender="Female")
        theirs = Appointment.objects.create(
            patient=other_patient, doctor=self.doctor, appointment_date=date(2030, 3, 1),
            appointment_time=time(11, 0), reason="Theirs")
        self.client.login(username="pat_ap", password=PASSWORD)
        response = self.client.get(reverse("appointments:detail", args=[theirs.pk]))
        self.assertEqual(response.status_code, 403)

    def test_patient_can_request_appointment(self):
        self.client.login(username="pat_ap", password=PASSWORD)
        response = self.client.post(reverse("appointments:request"), {
            "doctor": self.doctor.pk, "appointment_date": "2030-04-10",
            "appointment_time": "14:00", "reason": "Self request checkup",
            "notes": "Patient notes"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Appointment.objects.filter(reason="Self request checkup").exists())

