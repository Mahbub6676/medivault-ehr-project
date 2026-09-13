from django import forms

from accounts.utils import bootstrap_form

from .models import Billing


class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ["patient", "appointment", "amount", "description",
                  "payment_status", "payment_method", "issued_date", "paid_date"]
        widgets = {
            "issued_date": forms.DateInput(attrs={"type": "date"}),
            "paid_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["appointment"].required = False
        self.fields["patient"].queryset = self.fields["patient"].queryset.select_related("user")
        bootstrap_form(self, {
            "amount": "e.g. 150.00",
            "description": "e.g. Consultation fee + CBC lab test",
        })

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("payment_status") == Billing.STATUS_PAID and not cleaned.get("paid_date"):
            self.add_error("paid_date", "Please provide the payment date for a paid invoice.")
        return cleaned
