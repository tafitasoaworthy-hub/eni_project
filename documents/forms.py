from django import forms
from accounts.forms import BootstrapMixin
from .models import DocumentTemplate, DocumentRequest, GeneratedDocument


class DocumentTemplateForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = ["nom", "type_document", "corps"]
        widgets = {"corps": forms.Textarea(attrs={"rows": 10})}


class DocumentRequestForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = ["student", "type_document", "motif"]


class GenerateDocumentForm(BootstrapMixin, forms.Form):
    """Formulaire de génération d'un document pour un étudiant."""
    titre = forms.CharField(label="Titre du document", max_length=200)
    contenu = forms.CharField(label="Contenu", widget=forms.Textarea(attrs={"rows": 12}))
    valide = forms.BooleanField(label="Marquer comme validé par un responsable", required=False)
