from django.contrib import admin
from .models import (
    AnneeUniversitaire, Niveau, Departement, Filiere, Teacher, Student, Matiere,
)


@admin.register(AnneeUniversitaire)
class AnneeAdmin(admin.ModelAdmin):
    list_display = ("libelle", "courante", "date_debut", "date_fin")
    list_filter = ("courante",)


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle", "ordre")


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "responsable", "archived")
    list_filter = ("archived",)
    search_fields = ("nom", "code")


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "departement", "archived")
    list_filter = ("departement", "archived")
    search_fields = ("nom", "code")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom", "prenom", "specialite", "departement", "archived")
    list_filter = ("departement", "grade", "archived")
    search_fields = ("nom", "prenom", "matricule")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom", "prenom", "filiere", "niveau", "statut", "archived")
    list_filter = ("filiere", "niveau", "statut", "archived")
    search_fields = ("nom", "prenom", "matricule")


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "filiere", "niveau", "enseignant", "credits", "coefficient")
    list_filter = ("filiere", "niveau", "semestre", "archived")
    search_fields = ("nom", "code")
