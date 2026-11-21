"""Peuple la base avec des données de démonstration réalistes."""
import random
from datetime import time, date
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from core.models import (
    AnneeUniversitaire, Niveau, Departement, Filiere, Teacher, Student, Matiere,
)
from enrollments.models import Enrollment
from schedules.models import Seance
from documents.models import DocumentTemplate, DocumentRequest, DocumentType

NOMS = ["Kouassi", "Traoré", "Diallo", "Bamba", "Koné", "Yao", "Touré", "Cissé",
        "Ouattara", "Mensah", "N'Guessan", "Sow", "Fofana", "Aka", "Gbagbo",
        "Doumbia", "Camara", "Soro", "Bakayoko", "Konaté"]
PRENOMS_M = ["Jean", "Kofi", "Ibrahim", "Marc", "Yacou", "Serge", "Franck", "Aboubacar", "Éric", "Olivier"]
PRENOMS_F = ["Awa", "Fatou", "Marie", "Aïcha", "Grace", "Nadège", "Salimata", "Chantal", "Rokia", "Léa"]
SPECIALITES = ["Algorithmique", "Bases de données", "Réseaux", "Mathématiques",
               "Économie", "Droit", "Gestion", "Physique", "Marketing", "Comptabilité"]


class Command(BaseCommand):
    help = "Crée des données de démonstration pour la plateforme."

    def add_arguments(self, parser):
        parser.add_argument("--students", type=int, default=60)

    @transaction.atomic
    def handle(self, *args, **opts):
        self.stdout.write("Création des données de démonstration...")

        # --- Utilisateurs de base ---
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults=dict(first_name="Admin", last_name="Système",
                          email="admin@universite-eni.local", role=User.Role.ADMIN,
                          is_staff=True, is_superuser=True),
        )
        if created:
            admin.set_password("admin123"); admin.save()
            self.stdout.write("  Admin : admin / admin123")

        scol, created = User.objects.get_or_create(
            username="scolarite",
            defaults=dict(first_name="Agent", last_name="Scolarité",
                          email="scolarite@universite-eni.local", role=User.Role.SCOLARITE,
                          is_staff=True),
        )
        if created:
            scol.set_password("scolarite123"); scol.save()
            self.stdout.write("  Scolarité : scolarite / scolarite123")

        # --- Années universitaires ---
        a1, _ = AnneeUniversitaire.objects.get_or_create(
            libelle="2023-2024", defaults=dict(date_debut=date(2023, 9, 1), date_fin=date(2024, 7, 31)))
        a2, _ = AnneeUniversitaire.objects.get_or_create(
            libelle="2024-2025", defaults=dict(date_debut=date(2024, 9, 1), date_fin=date(2025, 7, 31), courante=True))
        a2.courante = True; a2.save()

        # --- Niveaux ---
        niveaux = {}
        for i, (code, lib) in enumerate([("L1", "Licence 1"), ("L2", "Licence 2"),
                                         ("L3", "Licence 3"), ("M1", "Master 1"), ("M2", "Master 2")], 1):
            n, _ = Niveau.objects.get_or_create(code=code, defaults=dict(libelle=lib, ordre=i))
            niveaux[code] = n

        # --- Départements & filières ---
        dept_data = {
            "Informatique": ["Génie Logiciel", "Réseaux et Systèmes", "Science des Données"],
            "Gestion": ["Finance-Comptabilité", "Marketing", "Management"],
            "Sciences": ["Mathématiques", "Physique"],
            "Droit": ["Droit Privé", "Droit Public"],
        }
        departements = {}
        filieres = {}
        for di, (dnom, fils) in enumerate(dept_data.items(), 1):
            dep, _ = Departement.objects.get_or_create(
                code=f"DEP{di}", defaults=dict(nom=f"Département {dnom}",
                description=f"Département des études en {dnom.lower()}."))
            departements[dnom] = dep
            for fi, fnom in enumerate(fils, 1):
                f, _ = Filiere.objects.get_or_create(
                    code=f"{dnom[:3].upper()}{fi}", defaults=dict(nom=fnom, departement=dep))
                filieres[fnom] = f

        # --- Enseignants (avec comptes) ---
        teachers = []
        for i in range(12):
            nom = random.choice(NOMS)
            prenom = random.choice(PRENOMS_M + PRENOMS_F)
            dep = random.choice(list(departements.values()))
            t, created = Teacher.objects.get_or_create(
                matricule=f"ENS{2024}{i:03d}",
                defaults=dict(nom=nom, prenom=prenom, specialite=random.choice(SPECIALITES),
                              grade=random.choice([g[0] for g in Teacher.GRADES]),
                              departement=dep, email=f"ens{i}@universite-eni.local"))
            if created:
                # compte enseignant pour le premier
                if i == 0:
                    u, c = User.objects.get_or_create(
                        username="enseignant",
                        defaults=dict(first_name=prenom, last_name=nom, role=User.Role.ENSEIGNANT))
                    if c:
                        u.set_password("enseignant123"); u.save()
                        self.stdout.write("  Enseignant : enseignant / enseignant123")
                    t.user = u; t.save()
                t.filieres.add(*random.sample(
                    [f for f in filieres.values() if f.departement == dep] or list(filieres.values()),
                    k=min(2, len([f for f in filieres.values() if f.departement == dep]) or 1)))
            teachers.append(t)

        # --- Matières ---
        matieres = []
        base_matieres = ["Introduction", "Approfondissement", "Projet", "Séminaire"]
        for f in filieres.values():
            for code, niv in [("L1", niveaux["L1"]), ("L2", niveaux["L2"]), ("L3", niveaux["L3"])]:
                for bm in base_matieres[:3]:
                    m, _ = Matiere.objects.get_or_create(
                        code=f"{f.code}-{code}-{bm[:3].upper()}",
                        defaults=dict(nom=f"{bm} {f.nom}", filiere=f, niveau=niv,
                                      enseignant=random.choice(teachers),
                                      credits=random.choice([3, 4, 6]),
                                      coefficient=random.choice([1, 2, 3]),
                                      semestre=random.choice(["S1", "S2"])))
                    matieres.append(m)

        # --- Étudiants + inscriptions ---
        nb = opts["students"]
        fil_list = list(filieres.values())
        created_students = 0
        for i in range(nb):
            genre = random.choice(["M", "F"])
            prenom = random.choice(PRENOMS_M if genre == "M" else PRENOMS_F)
            nom = random.choice(NOMS)
            fil = random.choice(fil_list)
            niv = random.choice([niveaux["L1"], niveaux["L2"], niveaux["L3"]])
            if Student.objects.filter(nom=nom, prenom=prenom, filiere=fil, niveau=niv).exists():
                continue
            s = Student.objects.create(
                nom=nom, prenom=prenom, genre=genre,
                date_naissance=date(random.randint(1998, 2006), random.randint(1, 12), random.randint(1, 28)),
                lieu_naissance="Abidjan", nationalite="Ivoirienne",
                email=f"etudiant{i}@universite-eni.local",
                telephone=f"07{random.randint(10000000, 99999999)}",
                filiere=fil, niveau=niv)
            created_students += 1
            # inscription année courante
            Enrollment.objects.get_or_create(
                student=s, annee=a2,
                defaults=dict(filiere=fil, niveau=niv,
                              type_inscription="NOUVELLE",
                              statut=random.choice(["VALIDEE", "VALIDEE", "VALIDEE", "EN_ATTENTE"]),
                              cree_par=scol))

        # compte étudiant lié au premier étudiant
        first = Student.objects.first()
        if first and not first.user:
            u, c = User.objects.get_or_create(
                username="etudiant",
                defaults=dict(first_name=first.prenom, last_name=first.nom, role=User.Role.ETUDIANT))
            if c:
                u.set_password("etudiant123"); u.save()
                self.stdout.write("  Étudiant : etudiant / etudiant123")
            first.user = u; first.save()

        # --- Emplois du temps (quelques séances) ---
        jours = [1, 2, 3, 4, 5]
        creneaux = [(time(8, 0), time(10, 0)), (time(10, 0), time(12, 0)),
                    (time(14, 0), time(16, 0)), (time(16, 0), time(18, 0))]
        for f in fil_list:
            niv = niveaux["L1"]
            fmats = [m for m in matieres if m.filiere == f and m.niveau == niv][:4]
            for idx, m in enumerate(fmats):
                jour = jours[idx % len(jours)]
                cre = creneaux[idx % len(creneaux)]
                Seance.objects.get_or_create(
                    annee=a2, filiere=f, niveau=niv, matiere=m,
                    jour=jour, heure_debut=cre[0], heure_fin=cre[1],
                    defaults=dict(enseignant=m.enseignant, salle=f"Salle {random.randint(1, 20)}",
                                  type_seance=random.choice(["CM", "TD", "TP"])))

        # --- Modèles de documents ---
        from documents.services import DEFAULT_BODIES
        for td, body in DEFAULT_BODIES.items():
            DocumentTemplate.objects.get_or_create(
                type_document=td,
                defaults=dict(nom=f"Modèle — {dict(DocumentType.choices)[td]}", corps=body))

        # --- Quelques demandes de documents ---
        for s in Student.objects.all()[:5]:
            DocumentRequest.objects.get_or_create(
                student=s, type_document=DocumentType.ATTESTATION,
                defaults=dict(motif="Demande de bourse", statut="EN_ATTENTE", demande_par=scol))

        self.stdout.write(self.style.SUCCESS(
            f"Terminé. {created_students} étudiants créés, "
            f"{Teacher.objects.count()} enseignants, {Matiere.objects.count()} matières."))
        self.stdout.write(self.style.SUCCESS(
            "Comptes : admin/admin123 · scolarite/scolarite123 · enseignant/enseignant123 · etudiant/etudiant123"))
