from django import forms
from django.forms import inlineformset_factory

from accounts.utils import bootstrap_form

from .models import Prescription, PrescriptionItem


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "doctor", "medical_record", "prescribed_date",
                  "instructions", "notes"]
        widgets = {
            "prescribed_date": forms.DateInput(attrs={"type": "date"}),
            "instructions": forms.Textarea(attrs={"rows": 2}),
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
        bootstrap_form(self, {"instructions": "e.g. Take after meals, drink plenty of water"})


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ["medicine_name", "dosage", "frequency", "duration",
                  "route", "special_instruction"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_form(self, {
            "medicine_name": "e.g. Amoxicillin",
            "dosage": "e.g. 500 mg",
            "frequency": "e.g. 1+0+1",
            "duration": "e.g. 7 days",
            "special_instruction": "e.g. After meal",
        })


#: Formset used with a little vanilla JavaScript to add / remove medicines.
PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True,
)
