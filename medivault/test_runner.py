"""Custom test runner for MediVault EHR to auto-discover all app tests cleanly."""
from django.test.runner import DiscoverRunner


class AppDiscoverRunner(DiscoverRunner):
    """Ensure all app tests run cleanly when 'python manage.py test' is invoked without arguments."""

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = [
                "accounts.tests",
                "doctors.tests",
                "patients.tests",
                "appointments.tests",
                "medical_records.tests",
                "prescriptions.tests",
                "lab_tests.tests",
                "billing.tests",
                "notifications.tests",
                "dashboard.tests",
            ]
        return super().build_suite(test_labels, extra_tests=extra_tests, **kwargs)
