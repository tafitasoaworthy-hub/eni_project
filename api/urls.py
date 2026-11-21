from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register("niveaux", views.NiveauViewSet, basename="niveau")
router.register("annees", views.AnneeViewSet, basename="annee")
router.register("departements", views.DepartementViewSet, basename="departement")
router.register("filieres", views.FiliereViewSet, basename="filiere")
router.register("enseignants", views.TeacherViewSet, basename="enseignant")
router.register("etudiants", views.StudentViewSet, basename="etudiant")
router.register("matieres", views.MatiereViewSet, basename="matiere")
router.register("inscriptions", views.EnrollmentViewSet, basename="inscription")
router.register("seances", views.SeanceViewSet, basename="seance")
router.register("modeles-documents", views.DocumentTemplateViewSet, basename="modele")
router.register("demandes-documents", views.DocumentRequestViewSet, basename="demande")
router.register("documents-generes", views.GeneratedDocumentViewSet, basename="document")
router.register("journal", views.AuditLogViewSet, basename="journal")

urlpatterns = [
    # Auth
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("auth/me/", views.me, name="me"),
    path("auth/password/", views.change_password, name="change_password"),

    # Dashboard
    path("dashboard/stats/", views.dashboard_stats, name="dashboard_stats"),
    path("mon-emploi-du-temps/", views.my_seances, name="my_seances"),

    # Enums / helpers
    path("enums/", views.enums, name="enums"),
    path("documents/defaults/", views.document_defaults, name="document_defaults"),

    # AI
    path("ia/chat/", views.ai_chat, name="ai_chat"),
    path("ia/recherche/", views.ai_search, name="ai_search"),
    path("ia/assistant/", views.ai_assistant, name="ai_assistant"),
    path("ia/analyse/", views.ai_analysis, name="ai_analysis"),
    path("ia/brouillon-document/", views.ai_draft_document, name="ai_draft_document"),

    path("", include(router.urls)),
]
