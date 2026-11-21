from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import log_action
from accounts.permissions import staff_required
from django.contrib.auth.decorators import login_required
from core.models import AnneeUniversitaire, Filiere, Niveau, Teacher, Student
from .models import Seance
from .forms import SeanceForm

HEURES = [f"{h:02d}:00" for h in range(8, 20)]


def _grid(seances):
    """Organise les séances en grille jour x créneau."""
    data = {j: [] for j, _ in Seance.JOURS}
    for s in seances:
        data[s.jour].append(s)
    return data


@staff_required
def schedule_list(request):
    annee = request.GET.get("annee", "")
    filiere = request.GET.get("filiere", "")
    niveau = request.GET.get("niveau", "")
    enseignant = request.GET.get("enseignant", "")

    qs = Seance.objects.select_related("matiere", "enseignant", "filiere", "niveau", "annee")
    current = AnneeUniversitaire.current()
    if annee:
        qs = qs.filter(annee_id=annee)
    elif current:
        qs = qs.filter(annee=current)
        annee = str(current.pk)
    if filiere:
        qs = qs.filter(filiere_id=filiere)
    if niveau:
        qs = qs.filter(niveau_id=niveau)
    if enseignant:
        qs = qs.filter(enseignant_id=enseignant)

    # conflict count
    conflicts = sum(1 for s in qs if s.conflicts())

    return render(request, "schedules/list.html", {
        "grid": _grid(qs), "jours": Seance.JOURS, "total": qs.count(),
        "annee": annee, "filiere": filiere, "niveau": niveau, "enseignant": enseignant,
        "annees": AnneeUniversitaire.objects.all(),
        "filieres": Filiere.objects.filter(archived=False),
        "niveaux": Niveau.objects.all(),
        "enseignants": Teacher.objects.filter(archived=False),
        "conflicts": conflicts,
    })


@staff_required
def schedule_detail(request, pk):
    s = get_object_or_404(Seance, pk=pk)
    return render(request, "schedules/detail.html", {"s": s, "conflicts": s.conflicts()})


@staff_required
def schedule_create(request):
    form = SeanceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        s = form.save()
        conflicts = s.conflicts()
        log_action(request, "CREATE", f"Séance créée : {s}", s)
        if conflicts:
            messages.warning(request, f"Séance créée, mais {len(conflicts)} conflit(s) d'horaire détecté(s).")
        else:
            messages.success(request, "Séance ajoutée à l'emploi du temps.")
        return redirect("schedules:detail", pk=s.pk)
    return render(request, "schedules/form.html", {"form": form, "titre": "Nouvelle séance"})


@staff_required
def schedule_edit(request, pk):
    s = get_object_or_404(Seance, pk=pk)
    form = SeanceForm(request.POST or None, instance=s)
    if request.method == "POST" and form.is_valid():
        s = form.save()
        log_action(request, "UPDATE", f"Séance modifiée : {s}", s)
        messages.success(request, "Séance mise à jour.")
        return redirect("schedules:detail", pk=s.pk)
    return render(request, "schedules/form.html", {"form": form, "titre": "Modifier la séance", "obj": s})


@staff_required
def schedule_delete(request, pk):
    s = get_object_or_404(Seance, pk=pk)
    if request.method == "POST":
        rep = str(s)
        s.delete()
        log_action(request, "DELETE", f"Séance supprimée : {rep}")
        messages.warning(request, "Séance supprimée.")
        return redirect("schedules:list")
    return render(request, "core/confirm_delete.html", {
        "obj": s, "type": "séance", "back": "schedules:list",
    })


@login_required
def my_schedule(request):
    """Emploi du temps personnel (étudiant ou enseignant connecté)."""
    user = request.user
    qs = Seance.objects.none()
    titre = "Mon emploi du temps"
    current = AnneeUniversitaire.current()
    if user.is_etudiant and hasattr(user, "student_profile"):
        st = user.student_profile
        qs = Seance.objects.filter(filiere=st.filiere, niveau=st.niveau)
        if current:
            qs = qs.filter(annee=current)
        titre = f"Emploi du temps — {st.full_name}"
    elif user.is_enseignant and hasattr(user, "teacher_profile"):
        qs = Seance.objects.filter(enseignant=user.teacher_profile)
        if current:
            qs = qs.filter(annee=current)
        titre = f"Emploi du temps — {user.teacher_profile.full_name}"
    qs = qs.select_related("matiere", "enseignant", "filiere", "niveau")
    return render(request, "schedules/my_schedule.html", {
        "grid": _grid(qs), "jours": Seance.JOURS, "titre": titre, "total": qs.count(),
    })
