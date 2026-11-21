from django.db import models
from django.conf import settings
from django.urls import reverse


class DocumentType(models.TextChoices):
    ATTESTATION = "ATTESTATION", "Attestation d'inscription"
    CERTIFICAT = "CERTIFICAT", "Certificat de scolarité"
    FICHE = "FICHE", "Fiche d'inscription"
    CONVOCATION = "CONVOCATION", "Convocation"
    ANNONCE = "ANNONCE", "Annonce"
    COURRIER = "COURRIER", "Courrier administratif"
    AUTRE = "AUTRE", "Autre"


class DocumentTemplate(models.Model):
    """Modèle de document réutilisable avec des variables {{ matricule }} etc."""
    nom = models.CharField(max_length=150)
    type_document = models.CharField(
        "Type", max_length=20, choices=DocumentType.choices,
        default=DocumentType.ATTESTATION,
    )
    corps = models.TextField(
        "Corps du modèle",
        help_text="Variables disponibles : {{ nom }}, {{ prenom }}, {{ matricule }}, "
                  "{{ filiere }}, {{ niveau }}, {{ annee }}, {{ date }}, {{ universite }}.",
    )
    archived = models.BooleanField("Archivé", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modèle de document"
        verbose_name_plural = "Modèles de documents"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class DocumentRequest(models.Model):
    """Demande de document administratif."""

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        VALIDEE = "VALIDEE", "Validée"
        REFUSEE = "REFUSEE", "Refusée"

    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, related_name="demandes_documents",
        verbose_name="Étudiant",
    )
    type_document = models.CharField(
        "Type de document", max_length=20, choices=DocumentType.choices,
        default=DocumentType.ATTESTATION,
    )
    motif = models.CharField("Motif", max_length=255, blank=True)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE,
    )
    demande_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="demandes_faites", verbose_name="Demandé par",
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="demandes_traitees", verbose_name="Traité par",
    )
    commentaire = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande de document"
        verbose_name_plural = "Demandes de documents"
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("documents:request_detail", args=[self.pk])

    def __str__(self):
        return f"{self.get_type_document_display()} — {self.student}"


class GeneratedDocument(models.Model):
    """Document généré (texte + éventuel PDF) et archivé."""
    student = models.ForeignKey(
        "core.Student", on_delete=models.CASCADE, related_name="documents",
        verbose_name="Étudiant",
    )
    demande = models.ForeignKey(
        DocumentRequest, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="documents",
    )
    type_document = models.CharField(
        "Type", max_length=20, choices=DocumentType.choices,
        default=DocumentType.ATTESTATION,
    )
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    valide = models.BooleanField("Validé par un responsable", default=False)
    genere_par_ia = models.BooleanField("Généré par IA", default=False)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="documents_crees",
    )
    archived = models.BooleanField("Archivé", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document généré"
        verbose_name_plural = "Documents générés"
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse("documents:generated_detail", args=[self.pk])

    def __str__(self):
        return f"{self.titre} — {self.student}"
