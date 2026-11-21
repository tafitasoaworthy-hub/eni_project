from django.contrib.auth import get_user_model, update_session_auth_hash
from django.db.models import Count
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import (
    AnneeUniversitaire, Niveau, Departement, Filiere, Teacher, Student, Matiere,
)
from enrollments.models import Enrollment
from schedules.models import Seance
from documents.models import DocumentTemplate, DocumentRequest, GeneratedDocument, DocumentType
from documents import services as docservices
from accounts.models import AuditLog, log_action
from aiassistant import services as ai

from . import serializers as S
from .permissions import (
    IsStaffMember, IsAdmin, StaffWriteAuthenticatedRead, AdminWriteStaffRead,
)

User = get_user_model()


# ============================= AUTH =============================
class LoginView(TokenObtainPairView):
    serializer_class = S.MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if resp.status_code == 200:
            username = request.data.get("username")
            try:
                log_action(None, "LOGIN", f"Connexion API de {username}")
            except Exception:
                pass
        return resp


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == "PATCH":
        u = request.user
        for f in ("first_name", "last_name", "email", "phone"):
            if f in request.data:
                setattr(u, f, request.data[f])
        u.save()
        log_action(request, "UPDATE", "Mise à jour du profil (self)")
    return Response(S.UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    old = request.data.get("old_password", "")
    new = request.data.get("new_password", "")
    if not request.user.check_password(old):
        return Response({"detail": "Ancien mot de passe incorrect."}, status=400)
    if len(new) < 6:
        return Response({"detail": "Le nouveau mot de passe est trop court (min. 6)."}, status=400)
    request.user.set_password(new)
    request.user.save()
    update_session_auth_hash(request, request.user)
    log_action(request, "PASSWORD", "Changement de mot de passe (API)")
    return Response({"detail": "Mot de passe modifié."})


# ============================= USERS =============================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("username")
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name", "email"]
    filterset_fields = ["role", "is_active"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return S.UserWriteSerializer
        return S.UserSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        log_action(self.request, "CREATE", f"Création utilisateur {obj.username}", obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request, "UPDATE", f"Modification utilisateur {obj.username}", obj)

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        u = self.get_object()
        if u == request.user:
            return Response({"detail": "Impossible de désactiver son propre compte."}, status=400)
        u.is_active = not u.is_active
        u.save(update_fields=["is_active"])
        log_action(request, "PERMISSION", f"Compte {u.username} actif={u.is_active}", u)
        return Response(S.UserSerializer(u).data)

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        u = self.get_object()
        new = request.data.get("new_password", "")
        if len(new) < 6:
            return Response({"detail": "Mot de passe trop court (min. 6)."}, status=400)
        u.set_password(new)
        u.save()
        log_action(request, "PASSWORD", f"Réinitialisation mot de passe {u.username}", u)
        return Response({"detail": "Mot de passe réinitialisé."})


# ======================= BASE VIEWSET (audit) =======================
class AuditedModelViewSet(viewsets.ModelViewSet):
    entity = "objet"

    def perform_create(self, serializer):
        obj = serializer.save()
        log_action(self.request, "CREATE", f"Création {self.entity} : {obj}", obj)

    def perform_update(self, serializer):
        obj = serializer.save()
        log_action(self.request, "UPDATE", f"Modification {self.entity} : {obj}", obj)

    def perform_destroy(self, instance):
        rep = str(instance)
        log_action(self.request, "DELETE", f"Suppression {self.entity} : {rep}")
        instance.delete()


# ======================= REFERENCE DATA =======================
class NiveauViewSet(AuditedModelViewSet):
    entity = "niveau"
    queryset = Niveau.objects.all()
    serializer_class = S.NiveauSerializer
    permission_classes = [AdminWriteStaffRead]
    pagination_class = None


class AnneeViewSet(AuditedModelViewSet):
    entity = "année"
    queryset = AnneeUniversitaire.objects.all()
    serializer_class = S.AnneeSerializer
    permission_classes = [AdminWriteStaffRead]
    pagination_class = None

    @action(detail=True, methods=["post"])
    def set_current(self, request, pk=None):
        a = self.get_object()
        a.courante = True
        a.save()
        log_action(request, "UPDATE", f"Année courante : {a}", a)
        return Response(S.AnneeSerializer(a).data)


class DepartementViewSet(AuditedModelViewSet):
    entity = "département"
    serializer_class = S.DepartementSerializer
    permission_classes = [AdminWriteStaffRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "code"]
    filterset_fields = ["archived"]

    def get_queryset(self):
        qs = Departement.objects.all()
        archived = self.request.query_params.get("archived")
        if archived in ("true", "false"):
            qs = qs.filter(archived=(archived == "true"))
        return qs

    @action(detail=True, methods=["post"])
    def toggle_archive(self, request, pk=None):
        d = self.get_object(); d.archived = not d.archived; d.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Département {d} archivé={d.archived}", d)
        return Response(S.DepartementSerializer(d).data)


class FiliereViewSet(AuditedModelViewSet):
    entity = "filière"
    serializer_class = S.FiliereSerializer
    permission_classes = [AdminWriteStaffRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "code"]

    def get_queryset(self):
        qs = Filiere.objects.select_related("departement")
        p = self.request.query_params
        if p.get("archived") in ("true", "false"):
            qs = qs.filter(archived=(p["archived"] == "true"))
        if p.get("departement"):
            qs = qs.filter(departement_id=p["departement"])
        return qs

    @action(detail=True, methods=["post"])
    def toggle_archive(self, request, pk=None):
        f = self.get_object(); f.archived = not f.archived; f.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Filière {f} archivée={f.archived}", f)
        return Response(S.FiliereSerializer(f).data)


class TeacherViewSet(AuditedModelViewSet):
    entity = "enseignant"
    serializer_class = S.TeacherSerializer
    permission_classes = [StaffWriteAuthenticatedRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "prenom", "matricule", "specialite"]

    def get_queryset(self):
        qs = Teacher.objects.select_related("departement")
        p = self.request.query_params
        if p.get("archived") in ("true", "false"):
            qs = qs.filter(archived=(p["archived"] == "true"))
        else:
            qs = qs.filter(archived=False)
        if p.get("departement"):
            qs = qs.filter(departement_id=p["departement"])
        return qs

    @action(detail=True, methods=["post"])
    def toggle_archive(self, request, pk=None):
        t = self.get_object(); t.archived = not t.archived; t.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Enseignant {t} archivé={t.archived}", t)
        return Response(S.TeacherSerializer(t).data)


class StudentViewSet(AuditedModelViewSet):
    entity = "étudiant"
    serializer_class = S.StudentSerializer
    permission_classes = [IsStaffMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "prenom", "matricule", "email"]

    def get_queryset(self):
        qs = Student.objects.select_related("filiere", "niveau")
        p = self.request.query_params
        if p.get("archived") in ("true", "false"):
            qs = qs.filter(archived=(p["archived"] == "true"))
        else:
            qs = qs.filter(archived=False)
        if p.get("filiere"):
            qs = qs.filter(filiere_id=p["filiere"])
        if p.get("niveau"):
            qs = qs.filter(niveau_id=p["niveau"])
        if p.get("statut"):
            qs = qs.filter(statut=p["statut"])
        return qs

    @action(detail=True, methods=["post"])
    def toggle_archive(self, request, pk=None):
        s = self.get_object(); s.archived = not s.archived; s.save(update_fields=["archived"])
        log_action(request, "ARCHIVE", f"Étudiant {s} archivé={s.archived}", s)
        return Response(S.StudentSerializer(s).data)

    @action(detail=True, methods=["get"])
    def enrollments(self, request, pk=None):
        s = self.get_object()
        qs = s.inscriptions.select_related("annee", "filiere", "niveau")
        return Response(S.EnrollmentSerializer(qs, many=True).data)


class MatiereViewSet(AuditedModelViewSet):
    entity = "matière"
    serializer_class = S.MatiereSerializer
    permission_classes = [StaffWriteAuthenticatedRead]
    filter_backends = [filters.SearchFilter]
    search_fields = ["nom", "code"]

    def get_queryset(self):
        qs = Matiere.objects.select_related("filiere", "niveau", "enseignant")
        p = self.request.query_params
        if p.get("archived") in ("true", "false"):
            qs = qs.filter(archived=(p["archived"] == "true"))
        else:
            qs = qs.filter(archived=False)
        if p.get("filiere"):
            qs = qs.filter(filiere_id=p["filiere"])
        if p.get("niveau"):
            qs = qs.filter(niveau_id=p["niveau"])
        return qs


class EnrollmentViewSet(AuditedModelViewSet):
    entity = "inscription"
    serializer_class = S.EnrollmentSerializer
    permission_classes = [IsStaffMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ["student__nom", "student__prenom", "student__matricule"]

    def get_queryset(self):
        qs = Enrollment.objects.select_related("student", "annee", "filiere", "niveau")
        p = self.request.query_params
        for f in ("annee", "filiere", "niveau", "statut"):
            if p.get(f):
                qs = qs.filter(**{f if f != "statut" else "statut": p[f]})
        return qs

    def perform_create(self, serializer):
        obj = serializer.save(cree_par=self.request.user)
        log_action(self.request, "CREATE", f"Inscription : {obj}", obj)

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        e = self.get_object()
        statut = request.data.get("statut")
        if statut in dict(Enrollment.Statut.choices):
            e.statut = statut
            e.save()
            log_action(request, "UPDATE", f"Statut inscription {e} -> {statut}", e)
        return Response(S.EnrollmentSerializer(e).data)


class SeanceViewSet(AuditedModelViewSet):
    entity = "séance"
    serializer_class = S.SeanceSerializer
    permission_classes = [StaffWriteAuthenticatedRead]

    def get_queryset(self):
        qs = Seance.objects.select_related("matiere", "enseignant", "filiere", "niveau", "annee")
        p = self.request.query_params
        for f in ("annee", "filiere", "niveau", "enseignant"):
            if p.get(f):
                qs = qs.filter(**{f + "_id": p[f]})
        return qs


class DocumentTemplateViewSet(AuditedModelViewSet):
    entity = "modèle"
    queryset = DocumentTemplate.objects.filter(archived=False)
    serializer_class = S.DocumentTemplateSerializer
    permission_classes = [IsStaffMember]
    pagination_class = None


class DocumentRequestViewSet(AuditedModelViewSet):
    entity = "demande"
    serializer_class = S.DocumentRequestSerializer
    permission_classes = [IsStaffMember]

    def get_queryset(self):
        qs = DocumentRequest.objects.select_related("student")
        if self.request.query_params.get("statut"):
            qs = qs.filter(statut=self.request.query_params["statut"])
        return qs

    def perform_create(self, serializer):
        obj = serializer.save(demande_par=self.request.user)
        log_action(self.request, "DOCUMENT", f"Demande document : {obj}", obj)

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        r = self.get_object()
        statut = request.data.get("statut")
        if statut in dict(DocumentRequest.Statut.choices):
            r.statut = statut; r.traite_par = request.user; r.save()
            log_action(request, "DOCUMENT", f"Demande {r} -> {statut}", r)
        return Response(S.DocumentRequestSerializer(r).data)


class GeneratedDocumentViewSet(AuditedModelViewSet):
    entity = "document"
    serializer_class = S.GeneratedDocumentSerializer
    permission_classes = [IsStaffMember]

    def get_queryset(self):
        qs = GeneratedDocument.objects.select_related("student")
        archived = self.request.query_params.get("archived")
        qs = qs.filter(archived=(archived == "true"))
        if self.request.query_params.get("student"):
            qs = qs.filter(student_id=self.request.query_params["student"])
        return qs

    def perform_create(self, serializer):
        obj = serializer.save(cree_par=self.request.user)
        log_action(self.request, "DOCUMENT", f"Document généré : {obj}", obj)

    @action(detail=True, methods=["post"])
    def validate(self, request, pk=None):
        d = self.get_object(); d.valide = True; d.save(update_fields=["valide"])
        log_action(request, "DOCUMENT", f"Document validé : {d}", d)
        return Response(S.GeneratedDocumentSerializer(d).data)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        d = self.get_object()
        pdf = docservices.generate_pdf(d.titre, d.contenu, d.student)
        log_action(request, "DOCUMENT", f"Téléchargement PDF : {d}", d)
        resp = HttpResponse(pdf, content_type="application/pdf")
        resp["Content-Disposition"] = f'inline; filename="{d.type_document}_{d.student.matricule}.pdf"'
        return resp


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = S.AuditLogSerializer
    permission_classes = [IsStaffMember]
    filter_backends = [filters.SearchFilter]
    search_fields = ["message", "user__username"]

    def get_queryset(self):
        qs = AuditLog.objects.select_related("user")
        if self.request.query_params.get("action"):
            qs = qs.filter(action=self.request.query_params["action"])
        return qs


# ======================= DASHBOARD =======================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    annee_id = request.query_params.get("annee")
    enrollments = Enrollment.objects.all()
    if annee_id:
        enrollments = enrollments.filter(annee_id=annee_id)
    par_filiere = list(Filiere.objects.filter(archived=False)
                       .annotate(nb=Count("etudiants")).values("nom", "nb").order_by("-nb")[:10])
    par_niveau = list(Niveau.objects.annotate(nb=Count("etudiants"))
                      .values("code", "nb").order_by("ordre"))
    par_annee = list(AnneeUniversitaire.objects.annotate(nb=Count("inscriptions"))
                     .values("libelle", "nb").order_by("libelle"))
    statut_labels = dict(DocumentRequest.Statut.choices)
    doc_stats = [{"statut": statut_labels.get(d["statut"], d["statut"]), "nb": d["nb"]}
                 for d in DocumentRequest.objects.values("statut").annotate(nb=Count("id"))]
    return Response({
        "cards": {
            "etudiants": Student.objects.filter(archived=False).count(),
            "enseignants": Teacher.objects.filter(archived=False).count(),
            "departements": Departement.objects.filter(archived=False).count(),
            "filieres": Filiere.objects.filter(archived=False).count(),
            "matieres": Matiere.objects.filter(archived=False).count(),
            "inscriptions": enrollments.count(),
            "inscriptions_validees": enrollments.filter(statut="VALIDEE").count(),
            "inscriptions_attente": enrollments.filter(statut="EN_ATTENTE").count(),
            "demandes": DocumentRequest.objects.count(),
            "demandes_attente": DocumentRequest.objects.filter(statut="EN_ATTENTE").count(),
            "documents": GeneratedDocument.objects.count(),
        },
        "par_filiere": par_filiere,
        "par_niveau": par_niveau,
        "par_annee": par_annee,
        "doc_stats": doc_stats,
    })


# ======================= AI =======================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    history = request.data.get("history", [])
    if not isinstance(history, list):
        history = []
    answer, via = ai.ask_chatbot(request.user, history)
    log_action(request, "AI", f"Chatbot API (openai={via})")
    return Response({"answer": answer, "via_openai": via})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_search(request):
    q = request.query_params.get("q", "").strip()
    if not q:
        return Response({"answer": "", "via_openai": False})
    answer, via = ai.smart_search(request.user, q)
    log_action(request, "AI", f"Recherche IA : {q[:60]} (openai={via})")
    return Response({"answer": answer, "via_openai": via})


@api_view(["POST"])
@permission_classes([IsStaffMember])
def ai_assistant(request):
    task = request.data.get("task", "courrier")
    instructions = request.data.get("instructions", "")
    result, via = ai.admin_assist(request.user, task, instructions)
    log_action(request, "AI", f"Assistant admin API ({task}, openai={via})")
    return Response({"result": result, "via_openai": via})


@api_view(["POST"])
@permission_classes([IsStaffMember])
def ai_analysis(request):
    focus = request.data.get("focus", "")
    result, via = ai.analyze_data(request.user, focus)
    log_action(request, "AI", f"Analyse IA API (openai={via})")
    return Response({"result": result, "via_openai": via})


@api_view(["POST"])
@permission_classes([IsStaffMember])
def ai_draft_document(request):
    type_label = request.data.get("type", "Document")
    info = request.data.get("info", "")
    consignes = request.data.get("consignes", "")
    result, via = ai.draft_document(request.user, type_label, info, consignes)
    log_action(request, "AI", f"Brouillon document IA API (openai={via})")
    return Response({"result": result, "via_openai": via})


@api_view(["GET"])
@permission_classes([IsStaffMember])
def document_defaults(request):
    """Renvoie un contenu pré-rempli pour un type de document / étudiant."""
    student_id = request.query_params.get("student")
    type_doc = request.query_params.get("type", DocumentType.ATTESTATION)
    try:
        student = Student.objects.get(pk=student_id)
    except Student.DoesNotExist:
        return Response({"detail": "Étudiant introuvable."}, status=404)
    annee = AnneeUniversitaire.current()
    ctx = docservices.build_context(student, annee)
    tpl = DocumentTemplate.objects.filter(type_document=type_doc, archived=False).first()
    body = tpl.corps if tpl else docservices.default_body(type_doc)
    titre = dict(DocumentType.choices).get(type_doc, "Document")
    return Response({"titre": titre, "contenu": docservices.render_template(body, ctx)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_seances(request):
    """Emploi du temps de l'utilisateur connecté (étudiant ou enseignant)."""
    user = request.user
    qs = Seance.objects.none()
    current = AnneeUniversitaire.current()
    if getattr(user, "is_etudiant", False) and hasattr(user, "student_profile"):
        st = user.student_profile
        qs = Seance.objects.filter(filiere=st.filiere, niveau=st.niveau)
    elif getattr(user, "is_enseignant", False) and hasattr(user, "teacher_profile"):
        qs = Seance.objects.filter(enseignant=user.teacher_profile)
    if current:
        qs = qs.filter(annee=current)
    qs = qs.select_related("matiere", "enseignant", "filiere", "niveau")
    return Response(S.SeanceSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def enums(request):
    """Expose les listes de choix utiles au frontend."""
    from core.models import Student as St, Teacher as Te
    return Response({
        "document_types": [{"value": v, "label": l} for v, l in DocumentType.choices],
        "enrollment_status": [{"value": v, "label": l} for v, l in Enrollment.Statut.choices],
        "enrollment_types": [{"value": v, "label": l} for v, l in Enrollment.Type.choices],
        "student_status": [{"value": v, "label": l} for v, l in St.STATUTS],
        "teacher_grades": [{"value": v, "label": l} for v, l in Te.GRADES],
        "genres": [{"value": v, "label": l} for v, l in St.GENRES],
        "semestres": [{"value": v, "label": l} for v, l in Matiere.SEMESTRES],
        "seance_types": [{"value": v, "label": l} for v, l in Seance.TYPES],
        "jours": [{"value": v, "label": l} for v, l in Seance.JOURS],
        "roles": [{"value": v, "label": l} for v, l in User.Role.choices],
        "audit_actions": [{"value": v, "label": l} for v, l in AuditLog.ACTIONS],
    })
