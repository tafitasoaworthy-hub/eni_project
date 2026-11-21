from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    # Demandes
    path("demandes/", views.request_list, name="request_list"),
    path("demandes/nouvelle/", views.request_create, name="request_create"),
    path("demandes/<int:pk>/", views.request_detail, name="request_detail"),
    path("demandes/<int:pk>/statut/<str:statut>/", views.request_set_status, name="request_set_status"),

    # Génération
    path("generer/etudiant/<int:student_pk>/", views.generate_for_student, name="generate"),
    path("generes/", views.generated_list, name="generated_list"),
    path("generes/<int:pk>/", views.generated_detail, name="generated_detail"),
    path("generes/<int:pk>/pdf/", views.generated_pdf, name="generated_pdf"),
    path("generes/<int:pk>/valider/", views.generated_validate, name="generated_validate"),
    path("generes/<int:pk>/archiver/", views.generated_archive, name="generated_archive"),

    # Modèles
    path("modeles/", views.template_list, name="template_list"),
    path("modeles/nouveau/", views.template_create, name="template_create"),
    path("modeles/<int:pk>/modifier/", views.template_edit, name="template_edit"),
]
