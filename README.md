# MediVault EHR
### MediVault — Electronic Health Record Management System
**Secure, Simple & Smart Healthcare Records**

MediVault EHR is a complete Electronic Health Record management system for hospitals and clinics, built with **Python + Django + SQLite** and **Bootstrap 5** templates.


It covers the whole patient journey:

```
Patient Registration → Appointment → Doctor Consultation → Medical Record →
Diagnosis → Prescription → Lab Test → Lab Result → Billing → Follow-up
```

---

## 1. Features

| Module | What it does |
|---|---|
| **Authentication** | Django login/logout, hashed passwords, role based dashboards, permission checks, 403 page |
| **Users** | Admin can create, edit, activate/deactivate any account (Admin, Doctor, Receptionist, Patient) |
| **Departments** | Create and edit hospital departments, doctor counts |
| **Doctors** | Doctor ID (`DOC-00001`), department, specialization, qualification, experience, fee, availability, bio |
| **Patients** | Patient ID (`PAT-00001`), demographics, blood group, allergies, chronic conditions, emergency contact, search/filter/pagination, print summary |
| **Appointments** | Appointment ID (`APT-00001`), scheduling with **doctor double-booking protection**, confirm / complete / cancel / no-show, filters by date, doctor and status |
| **Medical Records** | Record ID (`MR-00001`), chief complaint, symptoms, diagnosis, treatment plan, clinical notes, follow-up date, print view |
| **Prescriptions** | Prescription ID (`RX-00001`) with **multiple medicines** (dosage, frequency, duration, route, instruction) added/removed by vanilla JavaScript, print view |
| **Lab Tests** | Test ID (`LAB-00001`), request, result, reference range, Pending/Completed status |
| **Billing** | Invoice ID (`INV-00001`), amount, payment status/method, mark-as-paid, print invoice |
| **Notifications** | In-app notifications with unread badge in the navbar, mark one / mark all read |
| **Dashboards** | Separate Admin, Doctor, Receptionist and Patient dashboards with Chart.js statistics |
| **Django Admin** | All models registered with `list_display`, `search_fields`, `list_filter`, `ordering` |

---

## 2. Technology stack

* Python 3.11+
* Django 5 (Django ORM, Django authentication, Django templates, ModelForms)
* SQLite (`db.sqlite3`)
* HTML5 / CSS3 / **vanilla JavaScript** (no frameworks)
* Bootstrap 5 + Bootstrap Icons (CDN)
* Chart.js (CDN)

> No Node.js, React, Next.js, TypeScript, Tailwind, PostgreSQL or MongoDB is used anywhere.
> *(The small `package.json` in the repository root only exists so the online sandbox can
> launch `python manage.py runserver`; it has **no dependencies** and can be deleted.)*

---

## 3. Installation

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
#    Windows
venv\Scripts\activate
#    Linux / Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database
python manage.py makemigrations
python manage.py migrate

# 5. Load demo data
python manage.py seed_data

# 6. Run the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/>

### Environment variables (optional)

| Variable | Purpose |
|---|---|
| `MEDIVAULT_SECRET_KEY` | Django `SECRET_KEY` (a development fallback is used if unset) |
| `MEDIVAULT_DEBUG` | Set to `False` to disable debug mode |

```bash
export MEDIVAULT_SECRET_KEY="a-long-random-string"
export MEDIVAULT_DEBUG=False
```

---

## 4. Demo accounts — **DEMO ONLY**

All demo users share the password below. It is intentionally simple for the viva
demonstration and **must never be used in a real system**.

```
Password for every demo account:  Medivault@123
```

| Role | Username | E-mail |
|---|---|---|
| Admin | `admin` | admin@medivault.local |
| Doctor | `doctor1` (also `doctor2`, `doctor3`) | doctor@medivault.local |
| Receptionist | `reception1` (also `reception2`) | reception@medivault.local |
| Patient | `patient1` … `patient10` | patient@medivault.local |

You may log in with either the **username** or the **e-mail address**.

---

## 5. User roles

| Role | Permissions |
|---|---|
| **Admin** | Everything: users, doctors, patients, departments, appointments, records, prescriptions, lab tests, billing, statistics |
| **Doctor** | Own appointments and patients, create/edit medical records, prescriptions, lab tests, view patient history |
| **Receptionist** | Register/edit/search patients, create/edit/confirm/cancel appointments, basic billing |
| **Patient** | Own dashboard, profile, appointments, medical records, prescriptions, lab results, bills and notifications only |

A patient can **never** open another patient's data — every patient-facing view filters on
`request.user` and object-level checks raise `PermissionDenied` (403).

---

## 6. Project structure

```
medivault_ehr/
├── manage.py                 # Django CLI
├── requirements.txt          # Django only
├── README.md
├── medivault/                # project settings, urls, wsgi, asgi
├── accounts/                 # custom User model, login, users, seed_data command
├── patients/                 # Patient model, registration, profile, print summary
├── doctors/                  # Department + Doctor models and management
├── appointments/             # Appointment model, conflict protection, statuses
├── medical_records/          # MedicalRecord model (core clinical document)
├── prescriptions/            # Prescription + PrescriptionItem (multi-medicine)
├── lab_tests/                # LabTest model, results
├── billing/                  # Billing/invoice model, print invoice
├── notifications/            # Notification model + navbar context processor
├── dashboard/                # Role based dashboards with Chart.js
├── templates/                # base.html, home.html, 403/404/500, partials
├── static/                   # css/style.css, js/app.js
└── media/
```

### Main database relationships

```
User 1—1 Patient            User 1—1 Doctor            Department 1—* Doctor
Patient 1—* Appointment     Doctor 1—* Appointment
Patient 1—* MedicalRecord   Doctor 1—* MedicalRecord   Appointment 1—* MedicalRecord
MedicalRecord 1—* Prescription        Prescription 1—* PrescriptionItem
Patient/Doctor/MedicalRecord 1—* LabTest
Patient 1—* Billing         Appointment 1—* Billing    User 1—* Notification
```

---

## 7. Demo scenario for the viva

1. Login as `reception1` → register a new patient → create an appointment.
2. Login as `doctor1` → the appointment appears on the dashboard → open the patient profile
   → read medical history → create a medical record with diagnosis → create a prescription
   with several medicines → request a lab test → publish the lab result.
3. Login as `patient1` → dashboard shows the appointment, medical record, prescription,
   lab result and pending bill; notifications show every event.
4. Login as `admin` → dashboard statistics and charts, billing overview, user management.

---

## 8. Print pages

Browser printing (`Ctrl+P`) is supported through `@media print` rules for:

* Patient summary — `/patients/<id>/print/`
* Medical record — `/medical-records/<id>/print/`
* Prescription — `/prescriptions/<id>/print/`
* Invoice — `/billing/<id>/print/`

---

## 9. Testing

```bash
python manage.py test
```

The suite (33 tests) covers login, role permissions, patient creation, doctor creation,
appointment creation, appointment conflicts, medical record creation, prescription creation
with multiple medicines, lab tests, billing, notifications and **patient data isolation**.

---

## 10. Future improvements

* PDF export with a reporting library
* Appointment time-slot calendar with drag & drop
* Doctor availability validation against `available_days` / `available_time`
* E-mail / SMS reminders
* Upload of scanned reports and medical images
* Two-factor authentication and a complete audit trail
* REST API for a mobile client

## 11. Security & Compliance Architecture

MediVault EHR implements Role-Based Access Control (RBAC), automatic HIPAA-style Audit Trail logging for Protected Health Information (PHI) access, double-booking prevention for clinical appointments, and encrypted session management.

