"""Document content rendering and PDF generation."""
import io
import re
from datetime import date
from django.conf import settings

from .models import DocumentType


DEFAULT_BODIES = {
    DocumentType.ATTESTATION: (
        "Je soussigné(e), responsable de la scolarité de {{ universite }}, atteste que "
        "l'étudiant(e) {{ prenom }} {{ nom }}, portant le matricule {{ matricule }}, "
        "est régulièrement inscrit(e) en {{ niveau }} de la filière {{ filiere }} "
        "au titre de l'année universitaire {{ annee }}.\n\n"
        "La présente attestation est délivrée pour servir et valoir ce que de droit."
    ),
    DocumentType.CERTIFICAT: (
        "Le présent certificat de scolarité atteste que {{ prenom }} {{ nom }} "
        "(matricule {{ matricule }}) suit régulièrement les enseignements de "
        "{{ niveau }} — {{ filiere }} durant l'année universitaire {{ annee }} "
        "au sein de {{ universite }}.\n\n"
        "Fait pour servir et valoir ce que de droit."
    ),
    DocumentType.FICHE: (
        "FICHE D'INSCRIPTION\n\n"
        "Nom et prénom : {{ nom }} {{ prenom }}\n"
        "Matricule : {{ matricule }}\n"
        "Filière : {{ filiere }}\n"
        "Niveau : {{ niveau }}\n"
        "Année universitaire : {{ annee }}\n"
        "Établissement : {{ universite }}\n\n"
        "Signature de l'étudiant(e) :\t\tSignature de l'administration :"
    ),
}


def build_context(student, annee=None):
    annee_lib = ""
    if annee:
        annee_lib = str(annee)
    else:
        from core.models import AnneeUniversitaire
        cur = AnneeUniversitaire.current()
        annee_lib = str(cur) if cur else ""
    return {
        "nom": student.nom,
        "prenom": student.prenom,
        "matricule": student.matricule,
        "filiere": student.filiere.nom if student.filiere else "—",
        "niveau": student.niveau.code if student.niveau else "—",
        "annee": annee_lib,
        "date": date.today().strftime("%d/%m/%Y"),
        "universite": settings.UNIVERSITY_NAME,
    }


def render_template(body, context):
    """Replace {{ var }} placeholders."""
    def repl(match):
        key = match.group(1).strip()
        return str(context.get(key, match.group(0)))
    return re.sub(r"\{\{\s*(\w+)\s*\}\}", repl, body or "")


def default_body(type_document):
    return DEFAULT_BODIES.get(type_document, "")


def generate_pdf(titre, contenu, student=None):
    """Return PDF bytes for a document using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable,
    )
    import os

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=20 * mm, bottomMargin=20 * mm,
        leftMargin=22 * mm, rightMargin=22 * mm,
    )
    styles = getSampleStyleSheet()
    h_center = ParagraphStyle("hc", parent=styles["Title"], alignment=TA_CENTER, fontSize=15)
    sub = ParagraphStyle("sub", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9, textColor="#555555")
    body = ParagraphStyle("body", parent=styles["Normal"], alignment=TA_JUSTIFY, fontSize=11, leading=18)
    title_style = ParagraphStyle("t", parent=styles["Heading2"], alignment=TA_CENTER)

    story = []
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo.jpg")
    if os.path.exists(logo_path):
        try:
            story.append(Image(logo_path, width=28 * mm, height=28 * mm))
        except Exception:
            pass
    story.append(Paragraph(settings.UNIVERSITY_NAME.upper(), h_center))
    story.append(Paragraph("Service de la scolarité", sub))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color="#8b1a1a"))
    story.append(Spacer(1, 18))
    story.append(Paragraph(titre.upper(), title_style))
    story.append(Spacer(1, 16))
    for para in contenu.split("\n"):
        if para.strip():
            story.append(Paragraph(para.replace("\t", " &nbsp;&nbsp;&nbsp; "), body))
        else:
            story.append(Spacer(1, 10))
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"Fait à {settings.UNIVERSITY_SHORT}, le {date.today().strftime('%d/%m/%Y')}",
        ParagraphStyle("d", parent=styles["Normal"], alignment=2)))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Le Responsable de la scolarité",
                           ParagraphStyle("s", parent=styles["Normal"], alignment=2)))
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
