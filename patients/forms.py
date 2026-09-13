"""Patient registration / edit form (creates the login account too)."""
from django import forms
from django.contrib.auth import get_user_model

from accounts.utils import bootstrap_form

from .models import Patient

User = get_user_model()


class PatientForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)
    username = forms.CharField(max_length=50, help_text="Used by the patient to log in.")
    password = forms.CharField(
        widget=forms.PasswordInput, required=False,
        help_text="Required for new patients. Leave blank to keep the current password.",
    )

    class Meta:
        model = Patient
        fields = [
            "date_of_birth", "gender", "blood_group", "phone", "address",
            "emergency_contact_name", "emergency_contact_phone",
            "allergies", "chronic_conditions",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "chronic_conditions": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            user = self.instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["username"].initial = user.username
            self.fields["username"].disabled = True
        else:
            self.fields["password"].required = True
        bootstrap_form(self, {
            "phone": "e.g. +1 555 010 2030",
            "emergency_contact_name": "Relative / guardian name",
            "allergies": "e.g. Penicillin, Peanuts",
            "chronic_conditions": "e.g. Asthma",
        })

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        patient = super().save(commit=False)
        data = self.cleaned_data
        if patient.pk:
            user = patient.user
        else:
            user = User(username=data["username"], role=User.ROLE_PATIENT)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data.get("email", "")
        user.phone = data.get("phone", "")
        user.role = User.ROLE_PATIENT
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        patient.user = user
        if commit:
            patient.save()
        return patient
