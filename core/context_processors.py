from django.conf import settings


def app_context(request):
    """Expose common values to every template."""
    from core.models import AnneeUniversitaire
    annee = None
    try:
        annee = AnneeUniversitaire.current()
    except Exception:
        pass
    return {
        "UNIVERSITY_NAME": settings.UNIVERSITY_NAME,
        "UNIVERSITY_SHORT": settings.UNIVERSITY_SHORT,
        "OPENAI_ENABLED": settings.OPENAI_ENABLED,
        "annee_courante": annee,
    }
