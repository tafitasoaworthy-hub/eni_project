from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import log_action
from accounts.permissions import staff_required, admin_required
from .models import (
    AnneeUniversitaire, Niveau, Departement, Filiere, Teacher, Student, Matiere,
)
from .forms import (
    AnneeForm, NiveauForm, DepartementForm, FiliereForm,
    TeacherForm, StudentForm, MatiereForm,
)


def _paginate(request, qs, per_page=12):
    return Paginator(qs, per_page).get_page(request.GET.get("page"))


# =========================================================================
# ÉTUDIANTS
# =========================================================================
@staff_required
def student_list(request):
    q = request.GET.get("q", "").strip()
    filiere = request.GET.get("filiere", "")
    niveau = request.GET.get("niveau", "")
    statut = request.GET.get("statut", "")
    show_archived = request.GET.get("archived") == "1"

    students = Student.objects.select_related("filiere", "niveau")
    students = students.filter(archived=show_archived)
    if q:
        students = students.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q)
            | Q(matricule__icontains=q) | Q(email__icontains=q)
        )
    if filiere:
        students = students.filter(filiere_id=filiere)
    if niveau:
        students = students.filter(niveau_id=niveau)
    if statut:
        students = students.filter(statut=statut)

    return render(request, "core/student_list.html", {
        "page_obj": _paginate(request, students),
        "q": q, "filiere": filiere, "niveau": niveau, "statut": statut,
        "show_archived": show_archived,
        "filieres": Filiere.objects.filter(archived=False),
        "niveaux": Niveau.objects.all(),
        "statuts": Student.STATUTS,
        "total": students.count(),
    })


@staff_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "core/student_detail.html", {
        "student": student,
        "inscriptions": student.inscriptions.select_related("annee", "filiere", "niveau"),
        "documents": student.documents.filter(archived=False),
        "demandes": student.demandes_documents.all(),
    })


@staff_required
def student_create(request):
    form = StudentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        student = form.save()
        log_action(request, "CREATE", f"Ajout de l'étudiant {student}", student)
        messages.success(request, f"Étudiant {student.full_name} ajouté (matricule {student.matricule}).")
        return redirect(student)
    return render(request, "core/student_form.html", {"form": form, "titre": "Ajouter un étudiant"})


@staff_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, request.FILES or None, instance=student)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification de l'étudiant {student}", student)
        messages.success(request, "Informations mises à jour.")
        return redirect(student)
    return render(request, "core/student_form.html", {
        "form": form, "titre": f"Modifier {student.full_name}", "obj": student,
    })


@staff_required
def student_archive(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.archived = not student.archived
        student.save(update_fields=["archived"])
        etat = "archivé" if student.archived else "restauré"
        log_action(request, "ARCHIVE", f"Étudiant {student} {etat}", student)
        messages.success(request, f"Étudiant {etat}.")
        return redirect("core:student_list")
    return render(request, "core/confirm_archive.html", {
        "obj": student, "type": "étudiant", "back": "core:student_list",
    })


@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        rep = str(student)
        student.delete()
        log_action(request, "DELETE", f"Suppression définitive de l'étudiant {rep}")
        messages.warning(request, "Étudiant supprimé définitivement.")
        return redirect("core:student_list")
    return render(request, "core/confirm_delete.html", {
        "obj": student, "type": "étudiant", "back": "core:student_list",
    })


# =========================================================================
# ENSEIGNANTS
# =========================================================================
@staff_required
def teacher_list(request):
    q = request.GET.get("q", "").strip()
    departement = request.GET.get("departement", "")
    show_archived = request.GET.get("archived") == "1"
    teachers = Teacher.objects.select_related("departement").filter(archived=show_archived)
    if q:
        teachers = teachers.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q)
            | Q(matricule__icontains=q) | Q(specialite__icontains=q)
        )
    if departement:
        teachers = teachers.filter(departement_id=departement)
    return render(request, "core/teacher_list.html", {
        "page_obj": _paginate(request, teachers),
        "q": q, "departement": departement, "show_archived": show_archived,
        "departements": Departement.objects.filter(archived=False),
        "total": teachers.count(),
    })


@staff_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, "core/teacher_detail.html", {
        "teacher": teacher,
        "matieres": teacher.matieres.select_related("filiere", "niveau"),
        "seances": teacher.seances.select_related("matiere", "filiere", "niveau", "annee"),
    })


@staff_required
def teacher_create(request):
    form = TeacherForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        teacher = form.save()
        log_action(request, "CREATE", f"Ajout de l'enseignant {teacher}", teacher)
        messages.success(request, f"Enseignant {teacher.full_name} ajouté.")
        return redirect(teacher)
    return render(request, "core/teacher_form.html", {"form": form, "titre": "Ajouter un enseignant"})


@staff_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    form = TeacherForm(request.POST or None, instance=teacher)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification de l'enseignant {teacher}", teacher)
        messages.success(request, "Informations mises à jour.")
        return redirect(teacher)
    return render(request, "core/teacher_form.html", {
        "form": form, "titre": f"Modifier {teacher.full_name}", "obj": teacher,
    })


@staff_required
def teacher_archive(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.archived = not teacher.archived
        teacher.save(update_fields=["archived"])
        etat = "archivé" if teacher.archived else "restauré"
        log_action(request, "ARCHIVE", f"Enseignant {teacher} {etat}", teacher)
        messages.success(request, f"Enseignant {etat}.")
        return redirect("core:teacher_list")
    return render(request, "core/confirm_archive.html", {
        "obj": teacher, "type": "enseignant", "back": "core:teacher_list",
    })


@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        rep = str(teacher)
        teacher.delete()
        log_action(request, "DELETE", f"Suppression de l'enseignant {rep}")
        messages.warning(request, "Enseignant supprimé.")
        return redirect("core:teacher_list")
    return render(request, "core/confirm_delete.html", {
        "obj": teacher, "type": "enseignant", "back": "core:teacher_list",
    })


# =========================================================================
# DÉPARTEMENTS
# =========================================================================
@staff_required
def departement_list(request):
    q = request.GET.get("q", "").strip()
    show_archived = request.GET.get("archived") == "1"
    departements = Departement.objects.filter(archived=show_archived).annotate(
        nb_filieres=Count("filieres", distinct=True),
        nb_enseignants=Count("enseignants", distinct=True),
    )
    if q:
        departements = departements.filter(Q(nom__icontains=q) | Q(code__icontains=q))
    return render(request, "core/departement_list.html", {
        "page_obj": _paginate(request, departements), "q": q,
        "show_archived": show_archived, "total": departements.count(),
    })


@staff_required
def departement_detail(request, pk):
    dep = get_object_or_404(Departement, pk=pk)
    return render(request, "core/departement_detail.html", {
        "dep": dep,
        "filieres": dep.filieres.filter(archived=False),
        "enseignants": dep.enseignants.filter(archived=False),
    })


@admin_required
def departement_create(request):
    form = DepartementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        dep = form.save()
        log_action(request, "CREATE", f"Création du département {dep}", dep)
        messages.success(request, f"Département « {dep.nom} » créé.")
        return redirect(dep)
    return render(request, "core/simple_form.html", {"form": form, "titre": "Nouveau département", "back": "core:departement_list"})


@admin_required
def departement_edit(request, pk):
    dep = get_object_or_404(Departement, pk=pk)
    form = DepartementForm(request.POST or None, instance=dep)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification du département {dep}", dep)
        messages.success(request, "Département mis à jour.")
        return redirect(dep)
    return render(request, "core/simple_form.html", {"form": form, "titre": f"Modifier {dep.nom}", "back": "core:departement_list"})


@admin_required
def departement_archive(request, pk):
    dep = get_object_or_404(Departement, pk=pk)
    if request.method == "POST":
        dep.archived = not dep.archived
        dep.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Département {dep} archivé={dep.archived}", dep)
        messages.success(request, "Opération effectuée.")
        return redirect("core:departement_list")
    return render(request, "core/confirm_archive.html", {
        "obj": dep, "type": "département", "back": "core:departement_list",
    })


# =========================================================================
# FILIÈRES
# =========================================================================
@staff_required
def filiere_list(request):
    q = request.GET.get("q", "").strip()
    departement = request.GET.get("departement", "")
    show_archived = request.GET.get("archived") == "1"
    filieres = Filiere.objects.select_related("departement").filter(archived=show_archived).annotate(
        nb_etudiants=Count("etudiants", distinct=True),
    )
    if q:
        filieres = filieres.filter(Q(nom__icontains=q) | Q(code__icontains=q))
    if departement:
        filieres = filieres.filter(departement_id=departement)
    return render(request, "core/filiere_list.html", {
        "page_obj": _paginate(request, filieres), "q": q, "departement": departement,
        "show_archived": show_archived,
        "departements": Departement.objects.filter(archived=False),
        "total": filieres.count(),
    })


@staff_required
def filiere_detail(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    niveau = request.GET.get("niveau", "")
    etudiants = filiere.etudiants.filter(archived=False).select_related("niveau")
    if niveau:
        etudiants = etudiants.filter(niveau_id=niveau)
    return render(request, "core/filiere_detail.html", {
        "filiere": filiere, "etudiants": etudiants, "niveau": niveau,
        "niveaux": Niveau.objects.all(),
        "matieres": filiere.matieres.filter(archived=False),
    })


@admin_required
def filiere_create(request):
    form = FiliereForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        f = form.save()
        log_action(request, "CREATE", f"Création de la filière {f}", f)
        messages.success(request, f"Filière « {f.nom} » créée.")
        return redirect(f)
    return render(request, "core/simple_form.html", {"form": form, "titre": "Nouvelle filière", "back": "core:filiere_list"})


@admin_required
def filiere_edit(request, pk):
    f = get_object_or_404(Filiere, pk=pk)
    form = FiliereForm(request.POST or None, instance=f)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification de la filière {f}", f)
        messages.success(request, "Filière mise à jour.")
        return redirect(f)
    return render(request, "core/simple_form.html", {"form": form, "titre": f"Modifier {f.nom}", "back": "core:filiere_list"})


@admin_required
def filiere_archive(request, pk):
    f = get_object_or_404(Filiere, pk=pk)
    if request.method == "POST":
        f.archived = not f.archived
        f.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Filière {f} archivée={f.archived}", f)
        messages.success(request, "Opération effectuée.")
        return redirect("core:filiere_list")
    return render(request, "core/confirm_archive.html", {
        "obj": f, "type": "filière", "back": "core:filiere_list",
    })


# =========================================================================
# NIVEAUX
# =========================================================================
@admin_required
def niveau_list(request):
    niveaux = Niveau.objects.annotate(nb=Count("etudiants"))
    return render(request, "core/niveau_list.html", {"niveaux": niveaux})


@admin_required
def niveau_create(request):
    form = NiveauForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        n = form.save()
        log_action(request, "CREATE", f"Création du niveau {n}", n)
        messages.success(request, "Niveau créé.")
        return redirect("core:niveau_list")
    return render(request, "core/simple_form.html", {"form": form, "titre": "Nouveau niveau", "back": "core:niveau_list"})


@admin_required
def niveau_edit(request, pk):
    n = get_object_or_404(Niveau, pk=pk)
    form = NiveauForm(request.POST or None, instance=n)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification du niveau {n}", n)
        messages.success(request, "Niveau mis à jour.")
        return redirect("core:niveau_list")
    return render(request, "core/simple_form.html", {"form": form, "titre": f"Modifier {n}", "back": "core:niveau_list"})


# =========================================================================
# MATIÈRES / MODULES
# =========================================================================
@staff_required
def matiere_list(request):
    q = request.GET.get("q", "").strip()
    filiere = request.GET.get("filiere", "")
    niveau = request.GET.get("niveau", "")
    show_archived = request.GET.get("archived") == "1"
    matieres = Matiere.objects.select_related("filiere", "niveau", "enseignant").filter(archived=show_archived)
    if q:
        matieres = matieres.filter(Q(nom__icontains=q) | Q(code__icontains=q))
    if filiere:
        matieres = matieres.filter(filiere_id=filiere)
    if niveau:
        matieres = matieres.filter(niveau_id=niveau)
    return render(request, "core/matiere_list.html", {
        "page_obj": _paginate(request, matieres), "q": q, "filiere": filiere, "niveau": niveau,
        "show_archived": show_archived,
        "filieres": Filiere.objects.filter(archived=False),
        "niveaux": Niveau.objects.all(), "total": matieres.count(),
    })


@staff_required
def matiere_detail(request, pk):
    matiere = get_object_or_404(Matiere, pk=pk)
    return render(request, "core/matiere_detail.html", {"matiere": matiere})


@staff_required
def matiere_create(request):
    form = MatiereForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        m = form.save()
        log_action(request, "CREATE", f"Création de la matière {m}", m)
        messages.success(request, f"Matière « {m.nom} » créée.")
        return redirect(m)
    return render(request, "core/simple_form.html", {"form": form, "titre": "Nouvelle matière", "back": "core:matiere_list"})


@staff_required
def matiere_edit(request, pk):
    m = get_object_or_404(Matiere, pk=pk)
    form = MatiereForm(request.POST or None, instance=m)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification de la matière {m}", m)
        messages.success(request, "Matière mise à jour.")
        return redirect(m)
    return render(request, "core/simple_form.html", {"form": form, "titre": f"Modifier {m.nom}", "back": "core:matiere_list"})


@staff_required
def matiere_archive(request, pk):
    m = get_object_or_404(Matiere, pk=pk)
    if request.method == "POST":
        m.archived = not m.archived
        m.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Matière {m} archivée={m.archived}", m)
        messages.success(request, "Opération effectuée.")
        return redirect("core:matiere_list")
    return render(request, "core/confirm_archive.html", {
        "obj": m, "type": "matière", "back": "core:matiere_list",
    })


# =========================================================================
# ANNÉES UNIVERSITAIRES
# =========================================================================
@admin_required
def annee_list(request):
    annees = AnneeUniversitaire.objects.annotate(nb=Count("inscriptions"))
    return render(request, "core/annee_list.html", {"annees": annees})


@admin_required
def annee_create(request):
    form = AnneeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        a = form.save()
        log_action(request, "CREATE", f"Création de l'année {a}", a)
        messages.success(request, "Année universitaire créée.")
        return redirect("core:annee_list")
    return render(request, "core/simple_form.html", {"form": form, "titre": "Nouvelle année universitaire", "back": "core:annee_list"})


@admin_required
def annee_edit(request, pk):
    a = get_object_or_404(AnneeUniversitaire, pk=pk)
    form = AnneeForm(request.POST or None, instance=a)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_action(request, "UPDATE", f"Modification de l'année {a}", a)
        messages.success(request, "Année mise à jour.")
        return redirect("core:annee_list")
    return render(request, "core/simple_form.html", {"form": form, "titre": f"Modifier {a}", "back": "core:annee_list"})


@admin_required
def annee_set_current(request, pk):
    a = get_object_or_404(AnneeUniversitaire, pk=pk)
    a.courante = True
    a.save()
    log_action(request, "UPDATE", f"Année courante définie : {a}", a)
    messages.success(request, f"« {a} » est maintenant l'année courante.")
    return redirect("core:annee_list")
