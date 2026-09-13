"""Billing tests."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from patients.models import Patient

from .models import Billing

User = get_user_model()
PASSWORD = "Medivault@123"


class BillingTests(TestCase):
    def setUp(self):
        self.reception = User.objects.create_user(username="recep_b", password=PASSWORD,
                                                  role=User.ROLE_RECEPTIONIST)
        patient_user = User.objects.create_user(username="pat_b", password=PASSWORD,
                                                role=User.ROLE_PATIENT)
        self.patient = Patient.objects.create(user=patient_user, gender="Male")

    def test_receptionist_generates_invoice(self):
        self.client.login(username="recep_b", password=PASSWORD)
        response = self.client.post(reverse("billing:add"), {
            "patient": self.patient.pk, "amount": "1500.00",
            "description": "Consultation", "payment_status": "Pending",
            "payment_method": "", "issued_date": "2030-07-01", "paid_date": "",
        })
        self.assertEqual(response.status_code, 302)
        invoice = Billing.objects.get()
        self.assertTrue(invoice.invoice_id.startswith("INV-"))

    def test_mark_invoice_paid(self):
        invoice = Billing.objects.create(patient=self.patient, amount=500)
        self.client.login(username="recep_b", password=PASSWORD)
        self.client.get(reverse("billing:mark_paid", args=[invoice.pk]))
        invoice.refresh_from_db()
        self.assertEqual(invoice.payment_status, "Paid")
        self.assertIsNotNone(invoice.paid_date)

    def test_patient_cannot_create_invoice(self):
        self.client.login(username="pat_b", password=PASSWORD)
        self.assertEqual(self.client.get(reverse("billing:add")).status_code, 403)
