from django import forms

from accounts.utils import bootstrap_form

from .models import MedicalRecord


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            "patient", "doctor", "appointment", "visit_date", "chief_complaint",
            "symptoms", "diagnosis", "treatment_plan", "clinical_notes", "follow_up_date",
        ]
        widgets = {
            "visit_date": forms.DateInput(attrs={"type": "date"}),
            "follow_up_date": forms.DateInput(attrs={"type": "date"}),
            "symptoms": forms.Textarea(attrs={"rows": 3}),
            "diagnosis": forms.Textarea(attrs={"rows": 3}),
            "treatment_plan": forms.Textarea(attrs={"rows": 3}),
            "clinical_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop("doctor", None)
        super().__init__(*args, **kwargs)
        self.fields["appointment"].required = False
        self.fields["patient"].queryset = self.fields["patient"].queryset.select_related("user")
        if doctor is not None:
            # A doctor always records under their own name.
            self.fields["doctor"].initial = doctor
            self.fields["doctor"].disabled = True
            self.fields["appointment"].queryset = doctor.appointments.select_related(
                "patient__user"
            )
        bootstrap_form(self, {
            "chief_complaint": "e.g. Persistent cough for 5 days",
            "symptoms": "e.g. Fever, fatigue, sore throat",
            "diagnosis": "e.g. Acute bronchitis",
            "treatment_plan": "e.g. Rest, fluids, antibiotics for 5 days",
        })
