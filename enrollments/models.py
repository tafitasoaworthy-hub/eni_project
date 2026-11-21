from django.db import models
from django.conf import settings
from django.urls import reverse


class Enrollment(models.Model):
    """Inscription / réinscription d'un étudiant pour une année universitaire."""

    class Type(models.TextChoices):
        NOUVELLE = "NOUVELLE", "Nouvelle inscription"
        REINSCRIPTION = "REINSCRIPTION", "Réinscription"

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        VALIDEE = "VALIDEE", "Validée"
        REFUSEE = "REFUSEE", "Refusée"

    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, related_name="inscriptions",
        verbose_name="Étudiant",
    )
    annee = models.ForeignKey(
        "core.AnneeUniversitaire", on_delete=models.PROTECT,
        related_name="inscriptions", verbose_name="Année universitaire",
    )
    filiere = models.ForeignKey(
        "core.Filiere", on_delete=models.PROTECT, related_name="inscriptions",
        verbose_name="Filière",
    )
    niveau = models.ForeignKey(
        "core.Niveau", on_delete=models.PROTECT, related_name="inscriptions",
        verbose_name="Niveau",
    )
    type_inscription = models.CharField(
        "Type", max_length=20, choices=Type.choices, default=Type.NOUVELLE,
    )
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE,
    )
    date_inscription = models.DateField(auto_now_add=True)
    observation = models.TextField(blank=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="inscriptions_creees", verbose_name="Créé par",
    )

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ["-annee__libelle", "student__nom"]
        unique_together = ("student", "annee")

    def get_absolute_url(self):
        return reverse("enrollments:detail", args=[self.pk])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Keep the student's current situation in sync with a validated enrollment
        if self.statut == self.Statut.VALIDEE:
            s = self.student
            s.filiere = self.filiere
            s.niveau = self.niveau
            s.save(update_fields=["filiere", "niveau"])

    def __str__(self):
        return f"{self.student} — {self.annee} ({self.get_statut_display()})"
