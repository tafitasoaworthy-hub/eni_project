from django import forms
from accounts.forms import BootstrapMixin
from core.models import AnneeUniversitaire
from .models import Enrollment


class EnrollmentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "annee", "filiere", "niveau",
                  "type_inscription", "statut", "observation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            current = AnneeUniversitaire.current()
            if current:
                self.fields["annee"].initial = current.pk
