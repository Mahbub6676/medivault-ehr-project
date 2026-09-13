"""Forms for departments and doctors."""
from django import forms
from django.contrib.auth import get_user_model

from accounts.utils import bootstrap_form

from .models import Department, Doctor

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_form(self, {"name": "e.g. Cardiology"})


class DoctorForm(forms.ModelForm):
    """Creates the linked user account together with the doctor profile."""

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20, required=False)
    username = forms.CharField(max_length=50)
    password = forms.CharField(
        widget=forms.PasswordInput, required=False,
        help_text="Required for new doctors. Leave blank to keep the current password.",
    )

    class Meta:
        model = Doctor
        fields = [
            "department", "specialization", "qualification", "experience",
            "consultation_fee", "available_days", "available_time", "bio",
        ]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            user = self.instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["phone"].initial = user.phone
            self.fields["username"].initial = user.username
            self.fields["username"].disabled = True
        else:
            self.fields["password"].required = True
        bootstrap_form(self, {
            "specialization": "e.g. Interventional Cardiology",
            "qualification": "e.g. MBBS, FCPS",
            "available_days": "e.g. Mon, Wed, Fri",
            "available_time": "e.g. 09:00 - 14:00",
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
        doctor = super().save(commit=False)
        data = self.cleaned_data
        if doctor.pk:
            user = doctor.user
        else:
            user = User(username=data["username"], role=User.ROLE_DOCTOR)
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.phone = data.get("phone", "")
        user.role = User.ROLE_DOCTOR
        if data.get("password"):
            user.set_password(data["password"])
        user.save()
        doctor.user = user
        if commit:
            doctor.save()
        return doctor
