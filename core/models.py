from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    archived = models.BooleanField(default=False, verbose_name="Archivé")

    class Meta:
        abstract = True


class AnneeUniversitaire(TimeStamped):
    """Année universitaire, ex: 2024-2025."""
    libelle = models.CharField("Libellé", max_length=20, unique=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    courante = models.BooleanField("Année courante", default=False)

    class Meta:
        verbose_name = "Année universitaire"
        verbose_name_plural = "Années universitaires"
        ordering = ["-libelle"]

    def save(self, *args, **kwargs):
        if self.courante:
            AnneeUniversitaire.objects.exclude(pk=self.pk).update(courante=False)
        super().save(*args, **kwargs)

    @classmethod
    def current(cls):
        return cls.objects.filter(courante=True).first() or cls.objects.first()

    def __str__(self):
        return self.libelle


class Niveau(TimeStamped):
    """Niveau d'étude : L1, L2, L3, M1, M2 ..."""
    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField("Libellé", max_length=50)
    ordre = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        ordering = ["ordre", "code"]

    def __str__(self):
        return self.code


class Departement(TimeStamped):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    responsable = models.ForeignKey(
        "core.Teacher", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="departements_diriges", verbose_name="Responsable",
    )

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ["nom"]

    def get_absolute_url(self):
        return reverse("core:departement_detail", args=[self.pk])

    def __str__(self):
        return f"{self.nom}"


class Filiere(TimeStamped):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=150)
    departement = models.ForeignKey(
        Departement, on_delete=models.CASCADE, related_name="filieres",
        verbose_name="Département",
    )
    parcours = models.CharField("Parcours", max_length=150, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ["nom"]

    def get_absolute_url(self):
        return reverse("core:filiere_detail", args=[self.pk])

    def __str__(self):
        return f"{self.nom}"


class Teacher(TimeStamped):
    """Enseignant."""
    GRADES = [
        ("ASSISTANT", "Assistant"),
        ("MAITRE_ASSISTANT", "Maître-assistant"),
        ("MAITRE_CONF", "Maître de conférences"),
        ("PROFESSEUR", "Professeur"),
        ("VACATAIRE", "Vacataire"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="teacher_profile",
    )
    matricule = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    specialite = models.CharField("Spécialité", max_length=150, blank=True)
    grade = models.CharField(max_length=30, choices=GRADES, default="ASSISTANT")
    departement = models.ForeignKey(
        Departement, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="enseignants", verbose_name="Département",
    )
    filieres = models.ManyToManyField(
        Filiere, blank=True, related_name="enseignants", verbose_name="Filières",
    )

    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ["nom", "prenom"]

    @property
    def full_name(self):
        return f"{self.prenom} {self.nom}".strip()

    def get_absolute_url(self):
        return reverse("core:teacher_detail", args=[self.pk])

    def __str__(self):
        return f"{self.full_name} ({self.matricule})"


class Student(TimeStamped):
    """Étudiant."""
    GENRES = [("M", "Masculin"), ("F", "Féminin")]
    STATUTS = [
        ("ACTIF", "Actif"),
        ("SUSPENDU", "Suspendu"),
        ("DIPLOME", "Diplômé"),
        ("ABANDON", "Abandon"),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="student_profile",
    )
    matricule = models.CharField(max_length=30, unique=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    genre = models.CharField(max_length=1, choices=GENRES, default="M")
    date_naissance = models.DateField("Date de naissance", null=True, blank=True)
    lieu_naissance = models.CharField("Lieu de naissance", max_length=150, blank=True)
    nationalite = models.CharField("Nationalité", max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    adresse = models.CharField("Adresse", max_length=255, blank=True)
    photo = models.ImageField(upload_to="students/", blank=True, null=True)
    # Current academic situation (history kept in Enrollment)
    filiere = models.ForeignKey(
        Filiere, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="etudiants", verbose_name="Filière",
    )
    niveau = models.ForeignKey(
        Niveau, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="etudiants", verbose_name="Niveau",
    )
    statut = models.CharField(max_length=20, choices=STATUTS, default="ACTIF")

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ["nom", "prenom"]

    @property
    def full_name(self):
        return f"{self.prenom} {self.nom}".strip()

    def get_absolute_url(self):
        return reverse("core:student_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.matricule:
            year = timezone.now().year
            # temporary save to get a pk, then build matricule
            super().save(*args, **kwargs)
            self.matricule = f"ETU{year}{self.pk:04d}"
            kwargs["force_insert"] = False
            return super().save(update_fields=["matricule"])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.matricule})"


class Matiere(TimeStamped):
    """Matière / module."""
    SEMESTRES = [("S1", "Semestre 1"), ("S2", "Semestre 2")]
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=150)
    filiere = models.ForeignKey(
        Filiere, on_delete=models.CASCADE, related_name="matieres",
        verbose_name="Filière",
    )
    niveau = models.ForeignKey(
        Niveau, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="matieres", verbose_name="Niveau",
    )
    enseignant = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="matieres", verbose_name="Enseignant",
    )
    credits = models.PositiveSmallIntegerField("Crédits", default=3)
    coefficient = models.PositiveSmallIntegerField(default=1)
    semestre = models.CharField(max_length=2, choices=SEMESTRES, default="S1")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ["nom"]

    def get_absolute_url(self):
        return reverse("core:matiere_detail", args=[self.pk])

    def __str__(self):
        return f"{self.nom} ({self.code})"
