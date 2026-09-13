from django import forms
from django.utils import timezone

from accounts.utils import bootstrap_form

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "patient", "doctor", "appointment_date", "appointment_time",
            "reason", "status", "notes",
        ]
        widgets = {
            "appointment_date": forms.DateInput(attrs={"type": "date"}),
            "appointment_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "patient" in self.fields:
            self.fields["patient"].queryset = self.fields["patient"].queryset.select_related("user")
        if "doctor" in self.fields:
            self.fields["doctor"].queryset = self.fields["doctor"].queryset.select_related("user")
        bootstrap_form(self, {"reason": "e.g. Chest pain follow-up"})


    def clean(self):
        cleaned = super().clean()
        doctor = cleaned.get("doctor")
        date = cleaned.get("appointment_date")
        time = cleaned.get("appointment_time")

        if date and hasattr(date, "strftime") and date < timezone.localdate() and not self.instance.pk:
            raise forms.ValidationError("Appointment date cannot be in the past.")

        if doctor and date and hasattr(date, "strftime") and doctor.available_days:
            avail = doctor.available_days
            day_abbr = date.strftime("%a")
            day_full = date.strftime("%A")
            if not any(k in avail.lower() for k in ["daily", "everyday", "all"]):
                if day_abbr not in avail and day_full not in avail:
                    raise forms.ValidationError(
                        f"{doctor.full_name} is only available on: {doctor.available_days}. "
                        f"Selected date ({date.strftime('%Y-%m-%d')}, {day_full}) is off-schedule."
                    )

        if doctor and time and hasattr(time, "strftime") and doctor.available_time and "-" in doctor.available_time:
            parts = doctor.available_time.split("-")
            try:
                from datetime import datetime
                start_t = datetime.strptime(parts[0].strip(), "%H:%M").time()
                end_t = datetime.strptime(parts[1].strip(), "%H:%M").time()
                if not (start_t <= time <= end_t):
                    raise forms.ValidationError(
                        f"{doctor.full_name}'s consultation hours are {doctor.available_time}. "
                        f"Selected time ({time.strftime('%H:%M')}) is outside shift hours."
                    )
            except ValueError:
                pass


        if doctor and date and time:
            clash = Appointment.objects.filter(
                doctor=doctor, appointment_date=date, appointment_time=time
            ).exclude(pk=self.instance.pk)
            if clash.exists():
                raise forms.ValidationError(
                    "Conflict: this doctor already has an appointment on "
                    f"{date} at {time}. Please pick another slot."
                )
        return cleaned


class PatientAppointmentRequestForm(AppointmentForm):
    class Meta(AppointmentForm.Meta):
        fields = ["doctor", "appointment_date", "appointment_time", "reason", "notes"]


