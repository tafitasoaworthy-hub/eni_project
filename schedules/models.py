from django.db import models
from django.urls import reverse


class Seance(models.Model):
    """Séance d'emploi du temps."""

    JOURS = [
        (1, "Lundi"), (2, "Mardi"), (3, "Mercredi"),
        (4, "Jeudi"), (5, "Vendredi"), (6, "Samedi"),
    ]
    TYPES = [("CM", "Cours magistral"), ("TD", "Travaux dirigés"), ("TP", "Travaux pratiques")]

    annee = models.ForeignKey(
        "core.AnneeUniversitaire", on_delete=models.CASCADE, related_name="seances",
        verbose_name="Année universitaire",
    )
    filiere = models.ForeignKey(
        "core.Filiere", on_delete=models.CASCADE, related_name="seances",
        verbose_name="Filière",
    )
    niveau = models.ForeignKey(
        "core.Niveau", on_delete=models.CASCADE, related_name="seances",
        verbose_name="Niveau",
    )
    matiere = models.ForeignKey(
        "core.Matiere", on_delete=models.CASCADE, related_name="seances",
        verbose_name="Matière",
    )
    enseignant = models.ForeignKey(
        "core.Teacher", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="seances", verbose_name="Enseignant",
    )
    salle = models.CharField("Salle", max_length=50, blank=True)
    jour = models.PositiveSmallIntegerField("Jour", choices=JOURS, default=1)
    heure_debut = models.TimeField("Heure de début")
    heure_fin = models.TimeField("Heure de fin")
    type_seance = models.CharField("Type", max_length=2, choices=TYPES, default="CM")

    class Meta:
        verbose_name = "Séance"
        verbose_name_plural = "Séances (emploi du temps)"
        ordering = ["jour", "heure_debut"]

    def get_absolute_url(self):
        return reverse("schedules:detail", args=[self.pk])

    def overlaps(self, other):
        return (
            self.jour == other.jour
            and self.heure_debut < other.heure_fin
            and other.heure_debut < self.heure_fin
        )

    def conflicts(self):
        """Return a list of (type, seance) conflicts with this séance."""
        if not (self.heure_debut and self.heure_fin and self.annee_id):
            return []
        qs = Seance.objects.filter(annee=self.annee, jour=self.jour).exclude(pk=self.pk)
        found = []
        for other in qs:
            if not self.overlaps(other):
                continue
            if self.salle and other.salle and self.salle == other.salle:
                found.append(("salle", other))
            if self.enseignant_id and self.enseignant_id == other.enseignant_id:
                found.append(("enseignant", other))
            if self.filiere_id == other.filiere_id and self.niveau_id == other.niveau_id:
                found.append(("groupe", other))
        return found

    def __str__(self):
        return f"{self.get_jour_display()} {self.heure_debut:%H:%M} — {self.matiere}"
