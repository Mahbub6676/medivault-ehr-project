"""Seed sample data for MediVault EHR platform.

Usage:  python manage.py seed_data
"""

import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from appointments.models import Appointment
from billing.models import Billing
from doctors.models import Department, Doctor
from lab_tests.models import LabTest
from medical_records.models import MedicalRecord
from notifications.models import Notification, notify
from patients.models import Patient
from prescriptions.models import Prescription, PrescriptionItem

User = get_user_model()

DEMO_PASSWORD = "Medivault@123"   # DEMO ONLY - never use in production

DEPARTMENTS = [
    ("General Medicine", "Primary care, routine checkups and internal medicine."),
    ("Cardiology", "Heart and cardiovascular system care."),
    ("Pediatrics", "Healthcare for infants, children and adolescents."),
    ("Orthopedics", "Bones, joints, ligaments and muscle treatment."),
    ("Dermatology", "Skin, hair and nail conditions."),
]

DOCTORS = [
    ("doctor1", "Sarah", "Ahmed", "doctor@medivault.local", "Cardiology",
     "Interventional Cardiology", "MBBS, FCPS (Cardiology)", 12, 1200),
    ("doctor2", "Imran", "Khan", "doctor2@medivault.local", "General Medicine",
     "Internal Medicine", "MBBS, MD", 8, 800),
    ("doctor3", "Nadia", "Rahman", "doctor3@medivault.local", "Pediatrics",
     "Child Health", "MBBS, DCH", 6, 900),
]

RECEPTIONISTS = [
    ("reception1", "Fatima", "Noor", "reception@medivault.local"),
    ("reception2", "Hasan", "Ali", "reception2@medivault.local"),
]

PATIENTS = [
    ("patient1", "Ayesha", "Siddiqui", "patient@medivault.local", "Female", "O+", "1994-03-11"),
    ("patient2", "Rafiq", "Islam", "patient2@medivault.local", "Male", "A+", "1986-07-22"),
    ("patient3", "Maya", "Chowdhury", "patient3@medivault.local", "Female", "B+", "2001-01-05"),
    ("patient4", "Tanvir", "Hossain", "patient4@medivault.local", "Male", "AB+", "1978-11-30"),
    ("patient5", "Sadia", "Akter", "patient5@medivault.local", "Female", "O-", "1999-09-14"),
    ("patient6", "Kamal", "Uddin", "patient6@medivault.local", "Male", "B-", "1969-05-02"),
    ("patient7", "Rumi", "Begum", "patient7@medivault.local", "Female", "A-", "1990-12-19"),
    ("patient8", "Shakib", "Mahmud", "patient8@medivault.local", "Male", "O+", "2005-02-08"),
    ("patient9", "Nusrat", "Jahan", "patient9@medivault.local", "Female", "AB-", "1983-06-27"),
    ("patient10", "Arif", "Chowdhury", "patient10@medivault.local", "Male", "A+", "1996-08-16"),
]

COMPLAINTS = [
    ("Chest pain and shortness of breath", "Chest tightness, breathlessness on exertion",
     "Stable angina", "Beta blocker, low salt diet, weekly monitoring"),
    ("Persistent cough for one week", "Cough, mild fever, sore throat",
     "Acute bronchitis", "Antibiotics for 5 days, rest and warm fluids"),
    ("Severe headache and dizziness", "Throbbing headache, nausea, light sensitivity",
     "Migraine without aura", "Analgesics, sleep hygiene, trigger diary"),
    ("Joint pain in both knees", "Morning stiffness, swelling, reduced movement",
     "Early osteoarthritis", "Physiotherapy, weight control, pain relief gel"),
    ("Itchy skin rash on arms", "Red patches, itching, dry skin",
     "Contact dermatitis", "Topical steroid cream, avoid irritants"),
]

MEDICINES = [
    ("Amoxicillin", "500 mg", "1+0+1", "7 days", "Oral", "After meal"),
    ("Paracetamol", "500 mg", "1+1+1", "5 days", "Oral", "After meal"),
    ("Omeprazole", "20 mg", "1+0+0", "14 days", "Oral", "Before breakfast"),
    ("Atorvastatin", "10 mg", "0+0+1", "30 days", "Oral", "At night"),
    ("Cetirizine", "10 mg", "0+0+1", "10 days", "Oral", "At bedtime"),
    ("Salbutamol Inhaler", "2 puffs", "As needed", "30 days", "Inhalation", "During breathlessness"),
]

LAB_TESTS = [
    ("Complete Blood Count (CBC)", "4.0 - 11.0 x10^9/L", "WBC 8.2 x10^9/L, Hb 13.4 g/dL"),
    ("Lipid Profile", "LDL < 100 mg/dL", "LDL 142 mg/dL, HDL 48 mg/dL"),
    ("Blood Glucose (Fasting)", "70 - 100 mg/dL", "96 mg/dL"),
    ("Chest X-Ray", "Normal lung fields", "Mild bronchial wall thickening"),
    ("Thyroid Function Test", "TSH 0.4 - 4.0 mIU/L", "TSH 2.1 mIU/L"),
]


class Command(BaseCommand):
    help = "Populate the database with fake demo data for MediVault EHR."

    @transaction.atomic
    def handle(self, *args, **options):
        if Patient.objects.exists() or Doctor.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Demo data already exists - skipping seed. "
                "Delete db.sqlite3 and migrate again for a clean seed."
            ))
            return

        random.seed(42)
        today = timezone.localdate()

        # ---------------- Admin ----------------
        admin = self._user("admin", "System", "Administrator", "admin@medivault.local",
                           User.ROLE_ADMIN, staff=True, superuser=True)

        # ---------------- Departments ----------------
        departments = {}
        for name, description in DEPARTMENTS:
            departments[name] = Department.objects.create(name=name, description=description)

        # ---------------- Doctors ----------------
        doctors = []
        for username, first, last, email, dept, spec, qual, exp, fee in DOCTORS:
            user = self._user(username, first, last, email, User.ROLE_DOCTOR)
            doctors.append(Doctor.objects.create(
                user=user, department=departments[dept], specialization=spec,
                qualification=qual, experience=exp, consultation_fee=Decimal(fee),
                available_days="Sun, Tue, Thu", available_time="09:00 - 15:00",
                bio=f"{first} {last} is a {spec.lower()} specialist with {exp} years of experience.",
            ))

        # ---------------- Receptionists ----------------
        for username, first, last, email in RECEPTIONISTS:
            self._user(username, first, last, email, User.ROLE_RECEPTIONIST)

        # ---------------- Patients ----------------
        patients = []
        for username, first, last, email, gender, blood, dob in PATIENTS:
            user = self._user(username, first, last, email, User.ROLE_PATIENT)
            patients.append(Patient.objects.create(
                user=user,
                date_of_birth=date.fromisoformat(dob),
                gender=gender, blood_group=blood,
                phone=f"+8801{random.randint(100000000, 999999999)}",
                address=f"House {random.randint(1, 120)}, Road {random.randint(1, 20)}, Dhaka",
                emergency_contact_name=f"{last} Family",
                emergency_contact_phone=f"+8801{random.randint(100000000, 999999999)}",
                allergies=random.choice(["None", "Penicillin", "Dust, Pollen", "Seafood"]),
                chronic_conditions=random.choice(["None", "Hypertension", "Asthma", "Diabetes"]),
            ))

        # ---------------- Appointments / records / rx / labs / bills -------
        slots = [time(9, 0), time(10, 0), time(11, 0), time(12, 0), time(14, 0), time(15, 0)]
        used_slots = set()
        statuses = ["Scheduled", "Confirmed", "Completed", "Completed", "Cancelled"]

        for index, patient in enumerate(patients):
            doctor = doctors[index % len(doctors)]
            for visit in range(2):
                # pick a unique (doctor, date, time) combination
                while True:
                    day_offset = random.randint(-20, 12)
                    appointment_date = today + timedelta(days=day_offset)
                    slot = random.choice(slots)
                    key = (doctor.pk, appointment_date, slot)
                    if key not in used_slots:
                        used_slots.add(key)
                        break

                complaint, symptoms, diagnosis, plan = random.choice(COMPLAINTS)
                status = "Completed" if day_offset < 0 else random.choice(statuses)
                appointment = Appointment.objects.create(
                    patient=patient, doctor=doctor, appointment_date=appointment_date,
                    appointment_time=slot, reason=complaint, status=status,
                    notes="Demo appointment generated by seed_data.",
                )

                if status != "Completed":
                    continue

                record = MedicalRecord.objects.create(
                    patient=patient, doctor=doctor, appointment=appointment,
                    visit_date=appointment_date, chief_complaint=complaint,
                    symptoms=symptoms, diagnosis=diagnosis, treatment_plan=plan,
                    clinical_notes="Patient advised to return if symptoms worsen.",
                    follow_up_date=appointment_date + timedelta(days=14),
                )

                prescription = Prescription.objects.create(
                    patient=patient, doctor=doctor, medical_record=record,
                    prescribed_date=appointment_date,
                    instructions="Complete the full course. Drink plenty of water.",
                    notes="Demo prescription.",
                )
                for medicine in random.sample(MEDICINES, k=random.randint(2, 3)):
                    PrescriptionItem.objects.create(
                        prescription=prescription, medicine_name=medicine[0], dosage=medicine[1],
                        frequency=medicine[2], duration=medicine[3], route=medicine[4],
                        special_instruction=medicine[5],
                    )

                test_name, reference, result = random.choice(LAB_TESTS)
                completed = random.choice([True, False])
                LabTest.objects.create(
                    patient=patient, doctor=doctor, medical_record=record,
                    test_name=test_name, test_date=appointment_date,
                    reference_range=reference,
                    result=result if completed else "",
                    status="Completed" if completed else "Pending",
                    notes="Reviewed by the attending doctor." if completed else "",
                )

                paid = random.choice([True, False])
                Billing.objects.create(
                    patient=patient, appointment=appointment,
                    amount=doctor.consultation_fee + Decimal(random.randint(0, 900)),
                    description="Consultation fee and diagnostic services",
                    payment_status="Paid" if paid else "Pending",
                    payment_method=random.choice(["Cash", "Card", "Mobile Banking"]) if paid else "",
                    issued_date=appointment_date,
                    paid_date=appointment_date if paid else None,
                )

                notify(patient.user, "New medical record",
                       f"Record {record.record_id}: {diagnosis}", "RECORD")
                notify(patient.user, "New prescription issued",
                       f"Prescription {prescription.prescription_id} is ready.", "PRESCRIPTION")

        # A few extra notifications for the staff accounts
        notify(admin, "Welcome to MediVault EHR",
               "Demo data has been generated successfully.", "SYSTEM")
        for doctor in doctors:
            notify(doctor.user, "Your schedule is ready",
                   "Demo appointments have been assigned to you.", "APPOINTMENT")

        self.stdout.write(self.style.SUCCESS(
            "\nMediVault demo data created:\n"
            f"  Departments : {Department.objects.count()}\n"
            f"  Doctors     : {Doctor.objects.count()}\n"
            f"  Patients    : {Patient.objects.count()}\n"
            f"  Appointments: {Appointment.objects.count()}\n"
            f"  Records     : {MedicalRecord.objects.count()}\n"
            f"  Prescription: {Prescription.objects.count()}\n"
            f"  Lab tests   : {LabTest.objects.count()}\n"
            f"  Invoices    : {Billing.objects.count()}\n"
            f"  Notifications: {Notification.objects.count()}\n\n"
            f"Demo accounts (password: {DEMO_PASSWORD}) - DEMO ONLY:\n"
            "  admin / doctor1 / doctor2 / doctor3 / reception1 / reception2 / patient1..patient10\n"
        ))

    # ------------------------------------------------------------------
    def _user(self, username, first, last, email, role, staff=False, superuser=False):
        user = User(
            username=username, first_name=first, last_name=last, email=email,
            role=role, is_staff=staff or superuser, is_superuser=superuser,
            phone=f"+8801{random.randint(100000000, 999999999)}",
        )
        user.set_password(DEMO_PASSWORD)   # hashed by Django
        user.save()
        return user
