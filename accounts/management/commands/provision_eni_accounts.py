"""Create or update the four ENI login accounts without storing passwords in code."""
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User
from core.models import Student, Teacher


ACCOUNTS = (
    ("admineni@gmail.com", "ENI_ADMIN_PASSWORD", User.Role.ADMIN,
     "Administrateur", "ENI"),
    ("scolariteeni@gmail.com", "ENI_SCOLARITE_PASSWORD", User.Role.SCOLARITE,
     "Scolarité", "ENI"),
    ("enseignantseni@gamil.com", "ENI_ENSEIGNANT_PASSWORD", User.Role.ENSEIGNANT,
     "Enseignant", "ENI"),
    ("estudianteni@gmail.com", "ENI_ETUDIANT_PASSWORD", User.Role.ETUDIANT,
     "Étudiant", "ENI"),
)


class Command(BaseCommand):
    help = "Crée ou met à jour les quatre comptes de connexion ENI."

    def handle(self, *args, **options):
        passwords = {email: os.getenv(env_name) for email, env_name, *_ in ACCOUNTS}
        missing = [env_name for _, env_name, *_ in ACCOUNTS if not os.getenv(env_name)]
        if missing:
            raise CommandError(
                "Variables de mot de passe manquantes : " + ", ".join(missing)
            )

        with transaction.atomic():
            for email, env_name, role, first_name, last_name in ACCOUNTS:
                user = User.objects.filter(username=email).first()
                if user is None:
                    user = User.objects.filter(email__iexact=email).first()
                created = user is None
                if created:
                    user = User(username=email)

                user.username = email
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.role = role
                user.is_active = True
                user.is_superuser = role == User.Role.ADMIN
                user.is_staff = role in (User.Role.ADMIN, User.Role.SCOLARITE)
                user.set_password(passwords[email])
                user.save()

                if role == User.Role.ENSEIGNANT:
                    profile = Teacher.objects.filter(email__iexact=email).first()
                    if profile and (profile.user_id is None or profile.user_id == user.pk):
                        profile.user = user
                        profile.save(update_fields=["user"])
                elif role == User.Role.ETUDIANT:
                    profile = Student.objects.filter(email__iexact=email).first()
                    if profile and (profile.user_id is None or profile.user_id == user.pk):
                        profile.user = user
                        profile.save(update_fields=["user"])

                action = "créé" if created else "mis à jour"
                self.stdout.write(f"Compte {email} {action} ({user.get_role_display()}).")

        self.stdout.write(self.style.SUCCESS("Comptes ENI provisionnés."))
