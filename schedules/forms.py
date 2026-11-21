from django import forms
from accounts.forms import BootstrapMixin
from core.models import AnneeUniversitaire
from .models import Seance


class SeanceForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Seance
        fields = ["annee", "filiere", "niveau", "matiere", "enseignant",
                  "salle", "jour", "heure_debut", "heure_fin", "type_seance"]
        widgets = {
            "heure_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_fin": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            current = AnneeUniversitaire.current()
            if current:
                self.fields["annee"].initial = current.pk

    def clean(self):
        cleaned = super().clean()
        debut, fin = cleaned.get("heure_debut"), cleaned.get("heure_fin")
        if debut and fin and debut >= fin:
            raise forms.ValidationError("L'heure de début doit précéder l'heure de fin.")
        return cleaned
