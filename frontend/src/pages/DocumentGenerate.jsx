import { useEffect, useState } from "react";
import { useParams, useSearchParams, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useRefData } from "../data/RefDataContext";
import { PageHeader, Field, useToast, Loading } from "../components/ui";
import { Save, Bot, ArrowLeft } from "lucide-react";

export default function DocumentGenerate() {
  const { studentId } = useParams();
  const [sp] = useSearchParams();
  const nav = useNavigate();
  const toast = useToast();
  const { enums } = useRefData();
  const [student, setStudent] = useState(null);
  const [typeDoc, setTypeDoc] = useState(sp.get("type") || "ATTESTATION");
  const [titre, setTitre] = useState("");
  const [contenu, setContenu] = useState("");
  const [valide, setValide] = useState(false);
  const [aiUsed, setAiUsed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [drafting, setDrafting] = useState(false);

  useEffect(() => { api.get(`/etudiants/${studentId}/`).then(({ data }) => setStudent(data)); }, [studentId]);

  useEffect(() => {
    setLoading(true);
    api.get("/documents/defaults/", { params: { student: studentId, type: typeDoc } })
      .then(({ data }) => { setTitre(data.titre); setContenu(data.contenu); setAiUsed(null); })
      .finally(() => setLoading(false));
  }, [studentId, typeDoc]);

  async function aiDraft() {
    if (!student) return;
    setDrafting(true);
    const label = (enums.document_types || []).find((t) => t.value === typeDoc)?.label || "Document";
    const info = `Étudiant : ${student.full_name}, matricule ${student.matricule}, filière ${student.filiere_nom}, niveau ${student.niveau_code}.`;
    try {
      const { data } = await api.post("/ia/brouillon-document/", { type: label, info, consignes: contenu });
      setContenu(data.result); setAiUsed(data.via_openai);
      toast.info(data.via_openai ? "Brouillon OpenAI généré." : "Brouillon local généré.");
    } catch { toast.error("Génération IA impossible."); }
    finally { setDrafting(false); }
  }

  async function save() {
    try {
      const { data } = await api.post("/documents-generes/", {
        student: studentId, type_document: typeDoc, titre, contenu, valide, genere_par_ia: aiUsed === true,
      });
      toast.success("Document généré et archivé.");
      nav(`/documents`);
    } catch { toast.error("Enregistrement impossible."); }
  }

  if (!student) return <Loading />;

  return (
    <div>
      <button className="btn-ghost btn-sm mb-3" onClick={() => nav(-1)}><ArrowLeft className="h-4 w-4" /> Retour</button>
      <PageHeader title="Générer un document" subtitle={`${student.full_name} (${student.matricule})`} />

      <div className="mb-4 flex flex-wrap gap-2">
        {(enums.document_types || []).map((t) => (
          <button key={t.value} onClick={() => setTypeDoc(t.value)}
            className={`badge ${typeDoc === t.value ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
            {t.label}
          </button>
        ))}
      </div>

      {aiUsed !== null && (
        <div className={`mb-4 rounded-lg px-3 py-2 text-sm ${aiUsed ? "bg-sky-50 text-sky-700" : "bg-slate-100 text-slate-600"}`}>
          <Bot className="mr-1 inline h-4 w-4" />
          {aiUsed ? "Brouillon généré par OpenAI." : "Brouillon généré par le moteur local."} À vérifier et valider par un responsable avant délivrance.
        </div>
      )}

      <div className="card p-5">
        {loading ? <Loading /> : (
          <>
            <Field label="Titre du document"><input className="input" value={titre} onChange={(e) => setTitre(e.target.value)} /></Field>
            <Field label="Contenu" className="mt-3">
              <textarea className="textarea font-mono text-sm" rows={14} value={contenu} onChange={(e) => setContenu(e.target.value)} />
            </Field>
            <label className="mt-3 flex items-center gap-2 text-sm">
              <input type="checkbox" checked={valide} onChange={(e) => setValide(e.target.checked)} />
              Marquer comme validé par un responsable
            </label>
            <div className="mt-4 flex flex-wrap gap-2">
              <button className="btn-primary" onClick={save}><Save className="h-4 w-4" /> Enregistrer le document</button>
              <button className="btn-outline" onClick={aiDraft} disabled={drafting}><Bot className="h-4 w-4" /> {drafting ? "Génération..." : "Proposer un brouillon IA"}</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
