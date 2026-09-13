"""Authentication and user management forms."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .utils import bootstrap_form

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Login form that accepts either a username or an e-mail address."""

    username = forms.CharField(label="Username or e-mail")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_form(self, {
            "username": "admin or admin@medivault.local",
            "password": "Your password",
        })

    def clean_username(self):
        value = self.cleaned_data.get("username", "").strip()
        if "@" in value:
            user = User.objects.filter(email__iexact=value).first()
            if user:
                return user.username
        return value


class UserForm(forms.ModelForm):
    """Create / edit a system user (used by the Admin role)."""

    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=False,
        help_text="Leave empty when editing to keep the current password.",
    )
    password2 = forms.CharField(
        label="Confirm password", widget=forms.PasswordInput, required=False,
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone", "role", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_form(self)
        if not self.instance.pk:
            self.fields["password1"].required = True
            self.fields["password2"].required = True

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 or p2:
            if p1 != p2:
                self.add_error("password2", "The two password fields do not match.")
            elif len(p1) < 8:
                self.add_error("password1", "Password must be at least 8 characters long.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            # Django hashes the password for us - never store plain text.
            user.set_password(password)
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Every logged-in user can edit their own basic details."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrap_form(self)
