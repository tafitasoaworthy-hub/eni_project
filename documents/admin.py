from django.contrib import admin
from .models import DocumentTemplate, DocumentRequest, GeneratedDocument


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("nom", "type_document", "archived")
    list_filter = ("type_document", "archived")


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "type_document", "statut", "created_at")
    list_filter = ("type_document", "statut")
    search_fields = ("student__nom", "student__prenom", "student__matricule")


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ("titre", "student", "type_document", "valide", "genere_par_ia", "created_at")
    list_filter = ("type_document", "valide", "genere_par_ia", "archived")
