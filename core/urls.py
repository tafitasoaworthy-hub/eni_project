from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # Étudiants
    path("etudiants/", views.student_list, name="student_list"),
    path("etudiants/nouveau/", views.student_create, name="student_create"),
    path("etudiants/<int:pk>/", views.student_detail, name="student_detail"),
    path("etudiants/<int:pk>/modifier/", views.student_edit, name="student_edit"),
    path("etudiants/<int:pk>/archiver/", views.student_archive, name="student_archive"),
    path("etudiants/<int:pk>/supprimer/", views.student_delete, name="student_delete"),

    # Enseignants
    path("enseignants/", views.teacher_list, name="teacher_list"),
    path("enseignants/nouveau/", views.teacher_create, name="teacher_create"),
    path("enseignants/<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("enseignants/<int:pk>/modifier/", views.teacher_edit, name="teacher_edit"),
    path("enseignants/<int:pk>/archiver/", views.teacher_archive, name="teacher_archive"),
    path("enseignants/<int:pk>/supprimer/", views.teacher_delete, name="teacher_delete"),

    # Départements
    path("departements/", views.departement_list, name="departement_list"),
    path("departements/nouveau/", views.departement_create, name="departement_create"),
    path("departements/<int:pk>/", views.departement_detail, name="departement_detail"),
    path("departements/<int:pk>/modifier/", views.departement_edit, name="departement_edit"),
    path("departements/<int:pk>/archiver/", views.departement_archive, name="departement_archive"),

    # Filières
    path("filieres/", views.filiere_list, name="filiere_list"),
    path("filieres/nouvelle/", views.filiere_create, name="filiere_create"),
    path("filieres/<int:pk>/", views.filiere_detail, name="filiere_detail"),
    path("filieres/<int:pk>/modifier/", views.filiere_edit, name="filiere_edit"),
    path("filieres/<int:pk>/archiver/", views.filiere_archive, name="filiere_archive"),

    # Niveaux
    path("niveaux/", views.niveau_list, name="niveau_list"),
    path("niveaux/nouveau/", views.niveau_create, name="niveau_create"),
    path("niveaux/<int:pk>/modifier/", views.niveau_edit, name="niveau_edit"),

    # Matières
    path("matieres/", views.matiere_list, name="matiere_list"),
    path("matieres/nouvelle/", views.matiere_create, name="matiere_create"),
    path("matieres/<int:pk>/", views.matiere_detail, name="matiere_detail"),
    path("matieres/<int:pk>/modifier/", views.matiere_edit, name="matiere_edit"),
    path("matieres/<int:pk>/archiver/", views.matiere_archive, name="matiere_archive"),

    # Années universitaires
    path("annees/", views.annee_list, name="annee_list"),
    path("annees/nouvelle/", views.annee_create, name="annee_create"),
    path("annees/<int:pk>/modifier/", views.annee_edit, name="annee_edit"),
    path("annees/<int:pk>/definir-courante/", views.annee_set_current, name="annee_set_current"),
]
