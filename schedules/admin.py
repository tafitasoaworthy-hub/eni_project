from django.contrib import admin
from .models import Seance


@admin.register(Seance)
class SeanceAdmin(admin.ModelAdmin):
    list_display = ("jour", "heure_debut", "heure_fin", "matiere", "enseignant",
                    "filiere", "niveau", "salle", "type_seance")
    list_filter = ("annee", "filiere", "niveau", "jour", "type_seance")
