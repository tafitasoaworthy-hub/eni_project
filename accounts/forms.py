from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, UserCreationForm, PasswordChangeForm, SetPasswordForm,
)
from .models import User


class BootstrapMixin:
    """Add Bootstrap classes to every field widget."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            css = "form-check-input" if isinstance(
                w, (forms.CheckboxInput,)) else "form-select" if isinstance(
                w, (forms.Select, forms.SelectMultiple)) else "form-control"
            existing = w.attrs.get("class", "")
            w.attrs["class"] = (existing + " " + css).strip()


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class UserCreateForm(BootstrapMixin, UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email",
            "role", "phone", "password1", "password2", "is_active",
        ]


class UserEditForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email",
            "role", "phone", "is_active",
        ]


class ProfileForm(BootstrapMixin, forms.ModelForm):
    """Modification du profil par l'utilisateur lui-même."""
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "photo"]


class StyledPasswordChangeForm(BootstrapMixin, PasswordChangeForm):
    pass


class StyledSetPasswordForm(BootstrapMixin, SetPasswordForm):
    pass
