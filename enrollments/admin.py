from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "annee", "filiere", "niveau", "type_inscription", "statut")
    list_filter = ("annee", "filiere", "niveau", "statut", "type_inscription")
    search_fields = ("student__nom", "student__prenom", "student__matricule")
