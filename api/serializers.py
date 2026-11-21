from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import (
    AnneeUniversitaire, Niveau, Departement, Filiere, Teacher, Student, Matiere,
)
from enrollments.models import Enrollment
from schedules.models import Seance
from documents.models import DocumentTemplate, DocumentRequest, GeneratedDocument
from accounts.models import AuditLog

User = get_user_model()


# ----------------------------- Auth / Users ------------------------------
class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "full_name", "email",
                  "role", "role_display", "phone", "is_active", "is_superuser"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email",
                  "role", "phone", "is_active", "password"]

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        pwd = validated_data.pop("password", None) or get_random_string(10)
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user

    def update(self, instance, validated_data):
        pwd = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if pwd:
            instance.set_password(pwd)
        instance.save()
        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["name"] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


# ----------------------------- Reference data ----------------------------
class NiveauSerializer(serializers.ModelSerializer):
    nb_etudiants = serializers.IntegerField(source="etudiants.count", read_only=True)

    class Meta:
        model = Niveau
        fields = ["id", "code", "libelle", "ordre", "nb_etudiants"]


class AnneeSerializer(serializers.ModelSerializer):
    nb_inscriptions = serializers.IntegerField(source="inscriptions.count", read_only=True)

    class Meta:
        model = AnneeUniversitaire
        fields = ["id", "libelle", "date_debut", "date_fin", "courante", "nb_inscriptions"]


class DepartementSerializer(serializers.ModelSerializer):
    responsable_nom = serializers.CharField(source="responsable.full_name", read_only=True, default="")
    nb_filieres = serializers.IntegerField(source="filieres.count", read_only=True)
    nb_enseignants = serializers.IntegerField(source="enseignants.count", read_only=True)

    class Meta:
        model = Departement
        fields = ["id", "code", "nom", "description", "responsable", "responsable_nom",
                  "nb_filieres", "nb_enseignants", "archived"]


class FiliereSerializer(serializers.ModelSerializer):
    departement_nom = serializers.CharField(source="departement.nom", read_only=True)
    nb_etudiants = serializers.IntegerField(source="etudiants.count", read_only=True)

    class Meta:
        model = Filiere
        fields = ["id", "code", "nom", "departement", "departement_nom",
                  "parcours", "description", "nb_etudiants", "archived"]


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    grade_display = serializers.CharField(source="get_grade_display", read_only=True)
    departement_nom = serializers.CharField(source="departement.nom", read_only=True, default="")

    class Meta:
        model = Teacher
        fields = ["id", "matricule", "nom", "prenom", "full_name", "email", "telephone",
                  "specialite", "grade", "grade_display", "departement", "departement_nom",
                  "filieres", "archived"]


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    filiere_nom = serializers.CharField(source="filiere.nom", read_only=True, default="")
    niveau_code = serializers.CharField(source="niveau.code", read_only=True, default="")
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = Student
        fields = ["id", "matricule", "nom", "prenom", "full_name", "genre",
                  "date_naissance", "lieu_naissance", "nationalite", "email", "telephone",
                  "adresse", "filiere", "filiere_nom", "niveau", "niveau_code",
                  "statut", "statut_display", "archived"]
        read_only_fields = ["matricule"]


class MatiereSerializer(serializers.ModelSerializer):
    filiere_nom = serializers.CharField(source="filiere.nom", read_only=True)
    niveau_code = serializers.CharField(source="niveau.code", read_only=True, default="")
    enseignant_nom = serializers.CharField(source="enseignant.full_name", read_only=True, default="")
    semestre_display = serializers.CharField(source="get_semestre_display", read_only=True)

    class Meta:
        model = Matiere
        fields = ["id", "code", "nom", "filiere", "filiere_nom", "niveau", "niveau_code",
                  "enseignant", "enseignant_nom", "credits", "coefficient",
                  "semestre", "semestre_display", "description", "archived"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student_nom = serializers.CharField(source="student.full_name", read_only=True)
    student_matricule = serializers.CharField(source="student.matricule", read_only=True)
    annee_libelle = serializers.CharField(source="annee.libelle", read_only=True)
    filiere_nom = serializers.CharField(source="filiere.nom", read_only=True)
    niveau_code = serializers.CharField(source="niveau.code", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    type_display = serializers.CharField(source="get_type_inscription_display", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "student_nom", "student_matricule", "annee", "annee_libelle",
                  "filiere", "filiere_nom", "niveau", "niveau_code", "type_inscription",
                  "type_display", "statut", "statut_display", "date_inscription", "observation"]
        read_only_fields = ["date_inscription"]


class SeanceSerializer(serializers.ModelSerializer):
    matiere_nom = serializers.CharField(source="matiere.nom", read_only=True)
    enseignant_nom = serializers.CharField(source="enseignant.full_name", read_only=True, default="")
    filiere_nom = serializers.CharField(source="filiere.nom", read_only=True)
    niveau_code = serializers.CharField(source="niveau.code", read_only=True)
    jour_display = serializers.CharField(source="get_jour_display", read_only=True)
    type_display = serializers.CharField(source="get_type_seance_display", read_only=True)
    has_conflict = serializers.SerializerMethodField()

    class Meta:
        model = Seance
        fields = ["id", "annee", "filiere", "filiere_nom", "niveau", "niveau_code",
                  "matiere", "matiere_nom", "enseignant", "enseignant_nom", "salle",
                  "jour", "jour_display", "heure_debut", "heure_fin",
                  "type_seance", "type_display", "has_conflict"]

    def get_has_conflict(self, obj):
        return bool(obj.conflicts())


class DocumentTemplateSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_document_display", read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = ["id", "nom", "type_document", "type_display", "corps", "archived"]


class DocumentRequestSerializer(serializers.ModelSerializer):
    student_nom = serializers.CharField(source="student.full_name", read_only=True)
    student_matricule = serializers.CharField(source="student.matricule", read_only=True)
    type_display = serializers.CharField(source="get_type_document_display", read_only=True)
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)

    class Meta:
        model = DocumentRequest
        fields = ["id", "student", "student_nom", "student_matricule", "type_document",
                  "type_display", "motif", "statut", "statut_display", "commentaire", "created_at"]
        read_only_fields = ["created_at"]


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    student_nom = serializers.CharField(source="student.full_name", read_only=True)
    type_display = serializers.CharField(source="get_type_document_display", read_only=True)

    class Meta:
        model = GeneratedDocument
        fields = ["id", "student", "student_nom", "type_document", "type_display", "titre",
                  "contenu", "valide", "genere_par_ia", "archived", "created_at"]
        read_only_fields = ["created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True, default="système")
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "user_name", "action", "action_display", "message",
                  "ip_address", "created_at"]
