from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user with a role used for permission gating across the app."""

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        SCOLARITE = "SCOLARITE", "Scolarité / Administration"
        ENSEIGNANT = "ENSEIGNANT", "Enseignant"
        ETUDIANT = "ETUDIANT", "Étudiant"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.SCOLARITE
    )
    phone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # --- role helpers ---
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_scolarite(self):
        return self.role == self.Role.SCOLARITE

    @property
    def is_enseignant(self):
        return self.role == self.Role.ENSEIGNANT

    @property
    def is_etudiant(self):
        return self.role == self.Role.ETUDIANT

    @property
    def is_staff_member(self):
        """Admin or scolarité — the administrative back-office users."""
        return self.is_admin or self.is_scolarite

    def __str__(self):
        full = self.get_full_name()
        return f"{full or self.username} ({self.get_role_display()})"


class AuditLog(models.Model):
    """Journalisation des actions sensibles."""

    ACTIONS = [
        ("LOGIN", "Connexion"),
        ("LOGOUT", "Déconnexion"),
        ("LOGIN_FAILED", "Échec de connexion"),
        ("CREATE", "Création"),
        ("UPDATE", "Modification"),
        ("DELETE", "Suppression"),
        ("ARCHIVE", "Archivage"),
        ("PASSWORD", "Mot de passe"),
        ("PERMISSION", "Permission / rôle"),
        ("DOCUMENT", "Document"),
        ("AI", "Intelligence artificielle"),
        ("OTHER", "Autre"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=ACTIONS, default="OTHER")
    message = models.CharField(max_length=500)
    object_repr = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        who = self.user.username if self.user else "système"
        return f"[{self.created_at:%d/%m/%Y %H:%M}] {who} — {self.get_action_display()}"


def log_action(request, action, message, object_repr=""):
    """Helper to record an audit entry from a view."""
    ip = None
    user = None
    if request is not None:
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")
        if getattr(request, "user", None) and request.user.is_authenticated:
            user = request.user
    try:
        AuditLog.objects.create(
            user=user, action=action, message=message[:500],
            object_repr=str(object_repr)[:200], ip_address=ip,
        )
    except Exception:  # never let logging break a request
        pass
