from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import log_action
from accounts.permissions import staff_required
from core.models import AnneeUniversitaire, Filiere, Niveau
from .models import Enrollment
from .forms import EnrollmentForm


@staff_required
def enrollment_list(request):
    q = request.GET.get("q", "").strip()
    annee = request.GET.get("annee", "")
    filiere = request.GET.get("filiere", "")
    niveau = request.GET.get("niveau", "")
    statut = request.GET.get("statut", "")

    qs = Enrollment.objects.select_related("student", "annee", "filiere", "niveau")
    if q:
        qs = qs.filter(
            Q(student__nom__icontains=q) | Q(student__prenom__icontains=q)
            | Q(student__matricule__icontains=q)
        )
    if annee:
        qs = qs.filter(annee_id=annee)
    if filiere:
        qs = qs.filter(filiere_id=filiere)
    if niveau:
        qs = qs.filter(niveau_id=niveau)
    if statut:
        qs = qs.filter(statut=statut)

    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "enrollments/list.html", {
        "page_obj": page, "q": q, "annee": annee, "filiere": filiere,
        "niveau": niveau, "statut": statut,
        "annees": AnneeUniversitaire.objects.all(),
        "filieres": Filiere.objects.filter(archived=False),
        "niveaux": Niveau.objects.all(),
        "statuts": Enrollment.Statut.choices,
        "total": qs.count(),
    })


@staff_required
def enrollment_detail(request, pk):
    e = get_object_or_404(
        Enrollment.objects.select_related("student", "annee", "filiere", "niveau"), pk=pk)
    return render(request, "enrollments/detail.html", {"e": e})


@staff_required
def enrollment_create(request):
    form = EnrollmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        e = form.save(commit=False)
        e.cree_par = request.user
        try:
            e.save()
        except Exception:
            messages.error(request, "Cet étudiant a déjà une inscription pour cette année.")
            return render(request, "enrollments/form.html", {"form": form, "titre": "Nouvelle inscription"})
        log_action(request, "CREATE", f"Inscription créée : {e}", e)
        messages.success(request, "Inscription enregistrée.")
        return redirect(e)
    return render(request, "enrollments/form.html", {"form": form, "titre": "Nouvelle inscription"})


@staff_required
def enrollment_edit(request, pk):
    e = get_object_or_404(Enrollment, pk=pk)
    form = EnrollmentForm(request.POST or None, instance=e)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Inscription modifiée : {e}", e)
        messages.success(request, "Inscription mise à jour.")
        return redirect(e)
    return render(request, "enrollments/form.html", {"form": form, "titre": "Modifier l'inscription", "obj": e})


@staff_required
def enrollment_set_status(request, pk, statut):
    e = get_object_or_404(Enrollment, pk=pk)
    valid = dict(Enrollment.Statut.choices)
    if statut in valid:
        e.statut = statut
        e.save()
        log_action(request, "UPDATE", f"Statut inscription {e} -> {valid[statut]}", e)
        messages.success(request, f"Inscription marquée « {valid[statut]} ».")
    return redirect(e)
