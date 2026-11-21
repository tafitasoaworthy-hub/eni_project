# Plateforme de Gestion Universitaire — Université ENI

Application complète de gestion universitaire avec **intelligence artificielle (OpenAI + moteur de repli local)**.

- **Backend** : Django 5 + Django REST Framework (API REST, JWT) + **PostgreSQL** (SQLite en option)
- **Frontend** : React (Vite) + Tailwind CSS + React Router + Recharts
- **IA** : API OpenAI avec repli local automatique (fonctionne hors ligne)
- **Documents** : génération PDF (reportlab)

## Fonctionnalités

| Module | Détails |
|--------|---------|
| Authentification & utilisateurs | Connexion JWT, rôles (Admin, Scolarité, Enseignant, Étudiant), permissions, activation/désactivation, réinitialisation de mot de passe, journalisation |
| Étudiants | CRUD, matricule auto, recherche, filtres (filière/niveau/statut), archivage, profil détaillé, historique des inscriptions |
| Enseignants | CRUD, spécialités, grades, départements, matières, emploi du temps |
| Départements / Filières / Niveaux | CRUD, affectations, années universitaires |
| Matières / Modules | CRUD, crédits, coefficients, affectation enseignant |
| Inscriptions | Nouvelle/réinscription, statuts (en attente/validée/refusée), filtres |
| Emplois du temps | Création de séances, **détection de conflits** (salle/enseignant/groupe), vue par filière/enseignant, « mon emploi du temps » |
| Documents | Modèles, demandes, génération + **PDF**, validation, archivage |
| Tableau de bord | Statistiques + **graphiques dynamiques** (Recharts), filtrage par année |
| IA | Chatbot, recherche en langage naturel, assistant administratif, analyse des données, génération de brouillons |

## Prérequis
- Python 3.12+ et Node.js 18+
- **PostgreSQL** (par défaut). SQLite reste possible via `DB_ENGINE=sqlite`.

## Base de données PostgreSQL (WSL Kali)

Le projet utilise PostgreSQL. Installation dans WSL Kali (exécuter en root, sans mot de passe) :
```bash
wsl -d kali-linux -u root -- apt-get update
wsl -d kali-linux -u root -- apt-get install -y postgresql postgresql-contrib
wsl -d kali-linux -u root -- systemctl enable --now postgresql
```
Créer la base et le rôle applicatif :
```bash
wsl -d kali-linux -u root -- su - postgres -c "psql -c \"CREATE ROLE eni LOGIN PASSWORD 'eni2024' CREATEDB;\""
wsl -d kali-linux -u root -- su - postgres -c "createdb -O eni gestion_univ"
```
Le cluster écoute sur `127.0.0.1:5432` ; WSL2 relaie `localhost` depuis Windows,
donc Django (sur Windows) s'y connecte via `127.0.0.1:5432`. La configuration est
lue depuis `.env` (variables `POSTGRES_*`). Pour revenir à SQLite : `DB_ENGINE=sqlite`.

## Démarrage

### 1. Backend (API Django) — port 8000
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows ( source .venv/bin/activate sous Linux/Mac )
pip install -r requirements.txt
copy .env.example .env          # puis ajuster si besoin (DB, OpenAI)
python manage.py migrate
python manage.py seed            # données de démonstration + comptes
python manage.py runserver
```

### 2. Frontend (React) — port 5173
```bash
cd frontend
npm install
npm run dev
```
Puis ouvrir **http://localhost:5173**

## Comptes de démonstration
| Rôle | Identifiant | Mot de passe |
|------|-------------|--------------|
| Administrateur | `admin` | `admin123` |
| Scolarité | `scolarite` | `scolarite123` |
| Enseignant | `enseignant` | `enseignant123` |
| Étudiant | `etudiant` | `etudiant123` |

## Activer OpenAI (optionnel)
Copier `.env.example` en `.env` et renseigner :
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```
Sans clé, l'IA utilise automatiquement le **moteur local** (les modules IA restent fonctionnels).
La clé est lue côté serveur uniquement et n'est jamais exposée au frontend.

## Architecture
```
ENI_PROJECT/
├── config/            # Réglages Django, URLs, settings (DRF, JWT, CORS)
├── accounts/          # Utilisateur personnalisé, rôles, permissions, journal
├── core/              # Étudiants, enseignants, départements, filières, niveaux, matières, années
├── enrollments/       # Inscriptions
├── schedules/         # Emplois du temps + détection de conflits
├── documents/         # Modèles, demandes, génération PDF
├── aiassistant/       # Services IA (OpenAI + repli local)
├── dashboard/         # Statistiques (gabarits Django hérités)
├── api/               # API REST (serializers, viewsets, endpoints IA)
└── frontend/          # Application React (Vite + Tailwind)
```

> Note : des gabarits Django server-rendered existent aussi (sous `templates/`) ; le **frontend officiel est l'application React** qui consomme l'API REST sous `/api/`.

## Sécurité
Mots de passe hachés · permissions par rôle · protection CSRF/XSS (DRF) · requêtes ORM paramétrées
(anti-injection SQL) · clé OpenAI protégée côté serveur · journalisation des actions sensibles ·
l'IA n'expose que des données agrégées autorisées.
