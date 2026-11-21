from django import forms
from accounts.forms import BootstrapMixin
from .models import (
    AnneeUniversitaire, Niveau, Departement, Filiere, Teacher, Student, Matiere,
)


class AnneeForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = AnneeUniversitaire
        fields = ["libelle", "date_debut", "date_fin", "courante"]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }


class NiveauForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Niveau
        fields = ["code", "libelle", "ordre"]


class DepartementForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Departement
        fields = ["code", "nom", "responsable", "description"]


class FiliereForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Filiere
        fields = ["code", "nom", "departement", "parcours", "description"]


class TeacherForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "matricule", "nom", "prenom", "email", "telephone",
            "specialite", "grade", "departement", "filieres",
        ]
        widgets = {"filieres": forms.SelectMultiple(attrs={"size": 5})}


class StudentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "matricule", "nom", "prenom", "genre", "date_naissance",
            "lieu_naissance", "nationalite", "email", "telephone",
            "adresse", "photo", "filiere", "niveau", "statut",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "adresse": forms.TextInput(),
        }
        help_texts = {"matricule": "Laisser vide pour une génération automatique."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["matricule"].required = False


class MatiereForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Matiere
        fields = [
            "code", "nom", "filiere", "niveau", "enseignant",
            "credits", "coefficient", "semestre", "description",
        ]
