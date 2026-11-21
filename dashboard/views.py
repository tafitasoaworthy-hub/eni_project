import json
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from core.models import (
    Student, Teacher, Departement, Filiere, Niveau, Matiere, AnneeUniversitaire,
)
from enrollments.models import Enrollment
from documents.models import DocumentRequest, GeneratedDocument


def _stats(annee_id=None):
    students = Student.objects.filter(archived=False)
    enrollments = Enrollment.objects.all()
    if annee_id:
        enrollments = enrollments.filter(annee_id=annee_id)

    # Répartition étudiants par filière
    par_filiere = list(
        Filiere.objects.filter(archived=False)
        .annotate(nb=Count("etudiants", filter=None))
        .values("nom", "nb").order_by("-nb")[:10]
    )
    # Par niveau
    par_niveau = list(
        Niveau.objects.annotate(nb=Count("etudiants")).values("code", "nb").order_by("ordre")
    )
    # Inscriptions par année
    par_annee = list(
        AnneeUniversitaire.objects.annotate(nb=Count("inscriptions"))
        .values("libelle", "nb").order_by("libelle")
    )
    # Demandes de documents par statut
    doc_stats = list(
        DocumentRequest.objects.values("statut").annotate(nb=Count("id"))
    )
    statut_labels = dict(DocumentRequest.Statut.choices)
    doc_stats = [{"statut": statut_labels.get(d["statut"], d["statut"]), "nb": d["nb"]} for d in doc_stats]

    return {
        "nb_etudiants": students.count(),
        "nb_enseignants": Teacher.objects.filter(archived=False).count(),
        "nb_departements": Departement.objects.filter(archived=False).count(),
        "nb_filieres": Filiere.objects.filter(archived=False).count(),
        "nb_matieres": Matiere.objects.filter(archived=False).count(),
        "nb_inscriptions": enrollments.count(),
        "nb_inscriptions_validees": enrollments.filter(statut="VALIDEE").count(),
        "nb_inscriptions_attente": enrollments.filter(statut="EN_ATTENTE").count(),
        "nb_demandes": DocumentRequest.objects.count(),
        "nb_demandes_attente": DocumentRequest.objects.filter(statut="EN_ATTENTE").count(),
        "nb_documents": GeneratedDocument.objects.count(),
        "par_filiere": par_filiere,
        "par_niveau": par_niveau,
        "par_annee": par_annee,
        "doc_stats": doc_stats,
    }


@login_required
def home(request):
    user = request.user
    annee_id = request.GET.get("annee") or ""

    # Étudiant / enseignant get a lighter personal dashboard
    if user.is_etudiant:
        return render(request, "dashboard/student_home.html", {
            "profile": getattr(user, "student_profile", None),
        })
    if user.is_enseignant:
        tp = getattr(user, "teacher_profile", None)
        return render(request, "dashboard/teacher_home.html", {
            "profile": tp,
            "matieres": tp.matieres.all() if tp else [],
            "seances": tp.seances.all() if tp else [],
        })

    stats = _stats(annee_id or None)
    charts = {
        "filiere_labels": [x["nom"] for x in stats["par_filiere"]],
        "filiere_values": [x["nb"] for x in stats["par_filiere"]],
        "niveau_labels": [x["code"] for x in stats["par_niveau"]],
        "niveau_values": [x["nb"] for x in stats["par_niveau"]],
        "annee_labels": [x["libelle"] for x in stats["par_annee"]],
        "annee_values": [x["nb"] for x in stats["par_annee"]],
        "doc_labels": [x["statut"] for x in stats["doc_stats"]],
        "doc_values": [x["nb"] for x in stats["doc_stats"]],
    }
    return render(request, "dashboard/home.html", {
        "stats": stats,
        "charts_json": json.dumps(charts),
        "annees": AnneeUniversitaire.objects.all(),
        "annee_id": annee_id,
    })
