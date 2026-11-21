"""
Service IA : chatbot, assistant administratif, analyse de données, recherche
intelligente. Utilise l'API OpenAI si une clé est configurée, sinon un moteur
de repli local garantit le fonctionnement hors ligne (exigence 5.5).

Règle de confidentialité : l'IA n'expose que des informations agrégées et
publiques. Les données personnelles détaillées d'autres personnes ne sont pas
transmises au modèle (exigence 4.5 / 5.1).
"""
import logging
import re
from django.conf import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Contexte "métier" transmis au modèle (données agrégées uniquement)
# ---------------------------------------------------------------------------
def build_knowledge(user=None):
    from core.models import (
        Student, Teacher, Departement, Filiere, Niveau, Matiere, AnneeUniversitaire,
    )
    from enrollments.models import Enrollment

    annee = AnneeUniversitaire.current()
    lines = [
        f"Établissement : {settings.UNIVERSITY_NAME}.",
        f"Année universitaire courante : {annee.libelle if annee else 'non définie'}.",
        f"Nombre total d'étudiants actifs : {Student.objects.filter(archived=False).count()}.",
        f"Nombre total d'enseignants : {Teacher.objects.filter(archived=False).count()}.",
        f"Nombre de départements : {Departement.objects.filter(archived=False).count()}.",
        f"Nombre de filières : {Filiere.objects.filter(archived=False).count()}.",
        f"Nombre de matières : {Matiere.objects.filter(archived=False).count()}.",
        f"Nombre d'inscriptions enregistrées : {Enrollment.objects.count()}.",
    ]
    deps = Departement.objects.filter(archived=False)[:20]
    if deps:
        lines.append("Départements : " + ", ".join(d.nom for d in deps) + ".")
    fils = Filiere.objects.filter(archived=False).select_related("departement")[:30]
    if fils:
        lines.append("Filières par effectif :")
        for f in fils:
            nb = f.etudiants.filter(archived=False).count()
            lines.append(f"  - {f.nom} ({f.departement.nom}) : {nb} étudiants.")
    nivs = Niveau.objects.all()
    if nivs:
        lines.append("Niveaux : " + ", ".join(n.code for n in nivs) + ".")
    return "\n".join(lines)


PROCEDURES = {
    "inscription": (
        "Pour vous inscrire : rendez-vous au service de la scolarité avec une pièce "
        "d'identité, les relevés/diplômes requis, des photos d'identité et le reçu de "
        "paiement des droits. Le personnel crée votre dossier, vous affecte à une filière "
        "et à un niveau, puis valide l'inscription."
    ),
    "documents": (
        "Documents généralement nécessaires pour une inscription : pièce d'identité, "
        "diplôme ou relevé de notes, acte de naissance, photos d'identité et reçu de "
        "paiement. Pour une réinscription, le dossier de l'année précédente suffit souvent."
    ),
    "attestation": (
        "Pour obtenir une attestation d'inscription ou un certificat de scolarité, déposez "
        "une demande au service scolarité (ou via la plateforme). Après validation par un "
        "responsable, le document est généré au format PDF et peut être téléchargé."
    ),
    "emploi du temps": (
        "Votre emploi du temps est consultable dans la rubrique « Mon emploi du temps ». "
        "Il dépend de votre filière et de votre niveau pour l'année en cours."
    ),
    "reglement": (
        "Le règlement universitaire fixe l'assiduité, les conditions d'examen, le passage "
        "de niveau et la discipline. Rapprochez-vous de la scolarité pour le texte complet."
    ),
}

SYSTEM_PROMPT = (
    "Tu es l'assistant virtuel d'une plateforme de gestion universitaire. "
    "Tu réponds en français, de manière claire, polie et concise. Tu aides les "
    "étudiants et le personnel sur les inscriptions, les filières, les niveaux, les "
    "documents administratifs, les emplois du temps et les procédures. "
    "Utilise uniquement les informations fournies dans le contexte ; si une donnée "
    "n'y figure pas, invite l'utilisateur à contacter la scolarité. N'invente jamais "
    "de données personnelles."
)


def _openai_chat(messages, max_tokens=600, temperature=0.4):
    """Appel OpenAI protégé. Retourne (texte, True) ou lève une exception."""
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30)
    resp = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip(), True


# ---------------------------------------------------------------------------
# Recherche intelligente locale (repli) — interprète quelques questions types
# ---------------------------------------------------------------------------
def local_search(query, user=None):
    from core.models import Student, Teacher, Filiere, Niveau, Departement
    q = query.lower()

    # Combien d'enseignants ...
    if "enseignant" in q or "professeur" in q:
        nb = Teacher.objects.filter(archived=False).count()
        for d in Departement.objects.filter(archived=False):
            if d.nom.lower() in q:
                nbd = d.enseignants.filter(archived=False).count()
                return f"Le département « {d.nom} » compte {nbd} enseignant(s)."
        return f"Il y a actuellement {nb} enseignant(s) enregistré(s)."

    # Étudiants d'une filière / niveau
    niveau_match = re.search(r"\b([lm][12]|l3)\b", q)
    filiere_obj = None
    for f in Filiere.objects.filter(archived=False):
        if f.nom.lower() in q or (f.code and f.code.lower() in q):
            filiere_obj = f
            break

    if "étudiant" in q or "etudiant" in q or "effectif" in q or "inscrit" in q or "combien" in q:
        students = Student.objects.filter(archived=False)
        label = "au total"
        if filiere_obj:
            students = students.filter(filiere=filiere_obj)
            label = f"en filière {filiere_obj.nom}"
        if niveau_match:
            niv = Niveau.objects.filter(code__iexact=niveau_match.group(1)).first()
            if niv:
                students = students.filter(niveau=niv)
                label += f" niveau {niv.code}"
        nb = students.count()
        return f"Nombre d'étudiants {label} : {nb}."

    if filiere_obj:
        nb = filiere_obj.etudiants.filter(archived=False).count()
        return (f"Filière {filiere_obj.nom} (département {filiere_obj.departement.nom}) : "
                f"{nb} étudiants inscrits.")

    # Procédures
    for key, text in PROCEDURES.items():
        if key in q:
            return text

    return None


def local_chat_answer(query, user=None):
    ans = local_search(query, user)
    if ans:
        return ans
    ql = query.lower()
    for key, text in PROCEDURES.items():
        if key in ql or any(w in ql for w in key.split()):
            return text
    if any(w in ql for w in ("bonjour", "salut", "bonsoir", "coucou")):
        return "Bonjour ! Je suis l'assistant de la plateforme universitaire. Posez-moi une question sur les inscriptions, les filières, les documents ou les emplois du temps."
    if "aide" in ql or "aider" in ql or "comment" in ql:
        return ("Je peux vous renseigner sur : les inscriptions, les filières et niveaux, "
                "les documents administratifs (attestations, certificats), les emplois du "
                "temps et les procédures. Reformulez votre question avec un mot-clé.")
    return ("Je n'ai pas d'information précise sur ce point dans mes données. "
            "Pour une réponse officielle, contactez le service de la scolarité. "
            "Vous pouvez aussi me demander, par exemple : « Combien d'étudiants sont "
            "inscrits en informatique ? » ou « Quels documents pour une inscription ? ».")


# ---------------------------------------------------------------------------
# API publique du service
# ---------------------------------------------------------------------------
def ask_chatbot(user, history):
    """history : liste de dicts {role, content}. Retourne (reponse, via_openai)."""
    knowledge = build_knowledge(user)
    if settings.OPENAI_ENABLED:
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": "Contexte de l'établissement :\n" + knowledge},
            ] + history[-10:]
            return _openai_chat(messages)
        except Exception as e:  # indisponibilité API -> repli
            logger.warning("OpenAI indisponible, repli local : %s", e)
    last = history[-1]["content"] if history else ""
    return local_chat_answer(last, user), False


def admin_assist(user, task, instructions):
    """Assistant administratif : courriers, convocations, annonces, résumés."""
    task_prompts = {
        "courrier": "Rédige un courrier administratif universitaire formel.",
        "convocation": "Rédige une convocation universitaire officielle et concise.",
        "annonce": "Rédige une annonce universitaire claire à destination des étudiants.",
        "reformuler": "Reformule le texte suivant dans un style administratif professionnel.",
        "resumer": "Résume le texte suivant de manière concise et fidèle.",
        "reponse": "Propose une réponse polie et professionnelle à la demande administrative suivante.",
    }
    directive = task_prompts.get(task, "Aide à la rédaction administrative.")
    if settings.OPENAI_ENABLED:
        try:
            messages = [
                {"role": "system", "content":
                    "Tu es un assistant de rédaction administrative pour une université. "
                    "Tu écris en français, dans un style formel et professionnel. "
                    f"Établissement : {settings.UNIVERSITY_NAME}."},
                {"role": "user", "content": f"{directive}\n\nÉléments fournis :\n{instructions}"},
            ]
            return _openai_chat(messages, max_tokens=800, temperature=0.6)
        except Exception as e:
            logger.warning("OpenAI indisponible (assist), repli : %s", e)
    return _local_admin_assist(task, instructions), False


def _local_admin_assist(task, instructions):
    uni = settings.UNIVERSITY_NAME
    base = instructions.strip()
    if task == "resumer":
        phrases = re.split(r"(?<=[.!?])\s+", base)
        resume = " ".join(phrases[:3])
        return f"Résumé :\n{resume}" if resume else "Aucun contenu à résumer."
    if task == "reformuler":
        return (f"(Reformulation administrative)\n\nNous vous informons que : {base}\n\n"
                "Veuillez agréer, Madame, Monsieur, l'expression de nos salutations distinguées.")
    if task == "convocation":
        return (f"{uni}\nService de la scolarité\n\nOBJET : Convocation\n\n"
                f"Madame, Monsieur,\n\nVous êtes prié(e) de bien vouloir vous présenter "
                f"au service concerné. {base}\n\nComptant sur votre présence, veuillez agréer "
                "nos salutations distinguées.\n\nLe Responsable")
    if task == "annonce":
        return (f"ANNONCE — {uni}\n\nÀ l'attention de la communauté universitaire,\n\n{base}\n\n"
                "Merci de votre attention.\nL'administration")
    if task == "reponse":
        return (f"Madame, Monsieur,\n\nNous accusons réception de votre demande. {base}\n\n"
                "Notre service reviendra vers vous dans les meilleurs délais.\n\n"
                "Cordialement,\nLe service de la scolarité")
    # courrier par défaut
    return (f"{uni}\nService de la scolarité\n\nMadame, Monsieur,\n\n{base}\n\n"
            "Veuillez agréer, Madame, Monsieur, l'expression de nos salutations distinguées.\n\n"
            "Le Responsable de la scolarité")


def analyze_data(user, focus=""):
    """Analyse / synthèse en langage naturel des statistiques."""
    knowledge = build_knowledge(user)
    if settings.OPENAI_ENABLED:
        try:
            messages = [
                {"role": "system", "content":
                    "Tu es un analyste de données universitaires. À partir des chiffres "
                    "fournis, rédige une synthèse claire en français : tendances, "
                    "comparaisons entre filières, points d'attention. Sois factuel."},
                {"role": "user", "content":
                    f"Données :\n{knowledge}\n\nAxe d'analyse demandé : {focus or 'synthèse générale'}"},
            ]
            return _openai_chat(messages, max_tokens=700, temperature=0.5)
        except Exception as e:
            logger.warning("OpenAI indisponible (analyse), repli : %s", e)
    return _local_analysis(), False


def _local_analysis():
    from core.models import Student, Filiere, Teacher
    students = Student.objects.filter(archived=False)
    total = students.count()
    filieres = list(Filiere.objects.filter(archived=False))
    data = sorted(
        [(f.nom, f.etudiants.filter(archived=False).count()) for f in filieres],
        key=lambda x: -x[1],
    )
    lines = [f"Synthèse statistique — {settings.UNIVERSITY_NAME}", ""]
    lines.append(f"L'établissement compte {total} étudiants actifs, "
                 f"{Teacher.objects.filter(archived=False).count()} enseignants et "
                 f"{len(filieres)} filières.")
    if data:
        top = data[0]
        bottom = data[-1]
        lines.append(f"La filière la plus demandée est « {top[0]} » ({top[1]} étudiants), "
                     f"tandis que « {bottom[0]} » enregistre le plus faible effectif "
                     f"({bottom[1]} étudiants).")
        moyenne = round(total / len(data), 1) if data else 0
        lines.append(f"L'effectif moyen par filière est d'environ {moyenne} étudiants.")
        ecart = [f"{nom} : {nb}" for nom, nb in data[:5]]
        lines.append("Classement des filières (top 5) : " + " ; ".join(ecart) + ".")
    else:
        lines.append("Aucune filière renseignée pour le moment.")
    return "\n".join(lines)


def smart_search(user, query):
    """Recherche en langage naturel. Retourne (reponse, via_openai)."""
    local = local_search(query, user)
    if settings.OPENAI_ENABLED:
        try:
            knowledge = build_knowledge(user)
            messages = [
                {"role": "system", "content":
                    "Tu réponds à des questions sur des données universitaires en te basant "
                    "UNIQUEMENT sur le contexte fourni. Donne des chiffres précis si présents, "
                    "sinon indique que l'information n'est pas disponible. En français, concis."},
                {"role": "user", "content":
                    f"Contexte :\n{knowledge}\n\nCalcul local (indicatif) : {local or 'aucun'}\n\n"
                    f"Question : {query}"},
            ]
            return _openai_chat(messages, max_tokens=400, temperature=0.2)
        except Exception as e:
            logger.warning("OpenAI indisponible (recherche), repli : %s", e)
    return (local or local_chat_answer(query, user)), False


def draft_document(user, type_document, student_info, consignes=""):
    """Génère un brouillon de document administratif."""
    if settings.OPENAI_ENABLED:
        try:
            messages = [
                {"role": "system", "content":
                    "Tu rédiges des brouillons de documents administratifs universitaires "
                    "officiels en français. Style formel. Le document devra être vérifié et "
                    "validé par un responsable avant délivrance."},
                {"role": "user", "content":
                    f"Type de document : {type_document}\nInformations : {student_info}\n"
                    f"Consignes : {consignes}"},
            ]
            return _openai_chat(messages, max_tokens=700, temperature=0.5)
        except Exception as e:
            logger.warning("OpenAI indisponible (doc), repli : %s", e)
    return (f"[BROUILLON — à vérifier par un responsable]\n\n{type_document}\n\n{student_info}\n\n"
            f"{consignes}"), False
