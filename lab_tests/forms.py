from django import forms

from accounts.utils import bootstrap_form

from .models import LabTest


class LabTestForm(forms.ModelForm):
    class Meta:
        model = LabTest
        fields = ["patient", "doctor", "medical_record", "test_name", "test_date",
                  "result", "reference_range", "status", "notes"]
        widgets = {
            "test_date": forms.DateInput(attrs={"type": "date"}),
            "result": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)
        self.fields["medical_record"].required = False
        self.fields["patient"].queryset = self.fields["patient"].queryset.select_related("user")
        if doctor is not None:
            self.fields["doctor"].initial = doctor
            self.fields["doctor"].disabled = True
            self.fields["medical_record"].queryset = doctor.medical_records.select_related(
                "patient__user"
            )
        bootstrap_form(self, {
            "test_name": "e.g. Complete Blood Count (CBC)",
            "reference_range": "e.g. 4.0 - 11.0 x10^9/L",
            "result": "e.g. WBC 12.4 x10^9/L",
        })
