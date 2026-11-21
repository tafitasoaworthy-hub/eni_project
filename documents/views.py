from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import log_action
from accounts.permissions import staff_required
from core.models import Student, AnneeUniversitaire
from .models import DocumentTemplate, DocumentRequest, GeneratedDocument, DocumentType
from .forms import DocumentTemplateForm, DocumentRequestForm, GenerateDocumentForm
from . import services


# --- Demandes de documents ---
@staff_required
def request_list(request):
    statut = request.GET.get("statut", "")
    qs = DocumentRequest.objects.select_related("student")
    if statut:
        qs = qs.filter(statut=statut)
    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "documents/request_list.html", {
        "page_obj": page, "statut": statut, "statuts": DocumentRequest.Statut.choices,
        "total": qs.count(),
    })


@staff_required
def request_create(request):
    form = DocumentRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        req = form.save(commit=False)
        req.demande_par = request.user
        req.save()
        log_action(request, "DOCUMENT", f"Demande de document : {req}", req)
        messages.success(request, "Demande de document enregistrée.")
        return redirect("documents:request_detail", pk=req.pk)
    return render(request, "documents/request_form.html", {"form": form})


@staff_required
def request_detail(request, pk):
    req = get_object_or_404(DocumentRequest, pk=pk)
    return render(request, "documents/request_detail.html", {"req": req})


@staff_required
def request_set_status(request, pk, statut):
    req = get_object_or_404(DocumentRequest, pk=pk)
    valid = dict(DocumentRequest.Statut.choices)
    if statut in valid:
        req.statut = statut
        req.traite_par = request.user
        req.save()
        log_action(request, "DOCUMENT", f"Demande {req} -> {valid[statut]}", req)
        messages.success(request, f"Demande marquée « {valid[statut]} ».")
    return redirect("documents:request_detail", pk=req.pk)


# --- Génération de documents ---
@staff_required
def generate_for_student(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    type_doc = request.GET.get("type", DocumentType.ATTESTATION)
    annee = AnneeUniversitaire.current()
    ctx = services.build_context(student, annee)

    # pre-fill from a matching template, else default body
    tpl = DocumentTemplate.objects.filter(type_document=type_doc, archived=False).first()
    body = tpl.corps if tpl else services.default_body(type_doc)
    titre_default = dict(DocumentType.choices).get(type_doc, "Document")

    initial = {
        "titre": titre_default,
        "contenu": services.render_template(body, ctx),
    }
    form = GenerateDocumentForm(request.POST or None, initial=initial)
    ai_used = False
    if request.method == "POST":
        # Bouton « brouillon IA » : on régénère le contenu sans enregistrer
        if request.POST.get("action") == "ai_draft":
            from aiassistant import services as ai
            label = dict(DocumentType.choices).get(type_doc, "Document")
            info = (f"Étudiant : {ctx['prenom']} {ctx['nom']}, matricule {ctx['matricule']}, "
                    f"filière {ctx['filiere']}, niveau {ctx['niveau']}, année {ctx['annee']}.")
            draft, ai_used = ai.draft_document(request.user, label, info,
                                               request.POST.get("contenu", ""))
            log_action(request, "AI", f"Brouillon document IA ({label}, openai={ai_used})")
            form = GenerateDocumentForm(initial={
                "titre": request.POST.get("titre") or titre_default, "contenu": draft})
        elif form.is_valid():
            doc = GeneratedDocument.objects.create(
                student=student, type_document=type_doc,
                titre=form.cleaned_data["titre"], contenu=form.cleaned_data["contenu"],
                valide=form.cleaned_data["valide"], cree_par=request.user,
                genere_par_ia=request.POST.get("was_ai") == "1",
            )
            log_action(request, "DOCUMENT", f"Document généré : {doc}", doc)
            messages.success(request, "Document généré et archivé.")
            return redirect("documents:generated_detail", pk=doc.pk)
    return render(request, "documents/generate.html", {
        "form": form, "student": student, "type_doc": type_doc,
        "types": DocumentType.choices, "ai_used": ai_used,
    })


@staff_required
def generated_detail(request, pk):
    doc = get_object_or_404(GeneratedDocument, pk=pk)
    return render(request, "documents/generated_detail.html", {"doc": doc})


@staff_required
def generated_list(request):
    qs = GeneratedDocument.objects.select_related("student").filter(
        archived=request.GET.get("archived") == "1")
    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(request, "documents/generated_list.html", {
        "page_obj": page, "show_archived": request.GET.get("archived") == "1",
        "total": qs.count(),
    })


@staff_required
def generated_pdf(request, pk):
    doc = get_object_or_404(GeneratedDocument, pk=pk)
    pdf = services.generate_pdf(doc.titre, doc.contenu, doc.student)
    log_action(request, "DOCUMENT", f"Téléchargement PDF : {doc}", doc)
    resp = HttpResponse(pdf, content_type="application/pdf")
    fname = f"{doc.type_document}_{doc.student.matricule}.pdf"
    resp["Content-Disposition"] = f'inline; filename="{fname}"'
    return resp


@staff_required
def generated_validate(request, pk):
    doc = get_object_or_404(GeneratedDocument, pk=pk)
    doc.valide = True
    doc.save(update_fields=["valide"])
    log_action(request, "DOCUMENT", f"Document validé : {doc}", doc)
    messages.success(request, "Document validé par le responsable.")
    return redirect("documents:generated_detail", pk=doc.pk)


@staff_required
def generated_archive(request, pk):
    doc = get_object_or_404(GeneratedDocument, pk=pk)
    doc.archived = not doc.archived
    doc.save(update_fields=["archived"])
    messages.success(request, "Opération effectuée.")
    return redirect("documents:generated_list")


# --- Modèles de documents ---
@staff_required
def template_list(request):
    templates = DocumentTemplate.objects.filter(archived=False)
    return render(request, "documents/template_list.html", {"templates": templates})


@staff_required
def template_create(request):
    form = DocumentTemplateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        t = form.save()
        log_action(request, "DOCUMENT", f"Modèle créé : {t}", t)
        messages.success(request, "Modèle enregistré.")
        return redirect("documents:template_list")
    return render(request, "documents/template_form.html", {"form": form, "titre": "Nouveau modèle"})


@staff_required
def template_edit(request, pk):
    t = get_object_or_404(DocumentTemplate, pk=pk)
    form = DocumentTemplateForm(request.POST or None, instance=t)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Modèle mis à jour.")
        return redirect("documents:template_list")
    return render(request, "documents/template_form.html", {"form": form, "titre": f"Modifier {t.nom}"})
