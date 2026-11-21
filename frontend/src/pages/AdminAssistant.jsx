import { useState } from "react";
import api from "../api/client";
import { PageHeader, Spinner, useToast } from "../components/ui";
import { Wand2, Copy, AlertTriangle } from "lucide-react";

const TASKS = [
  ["courrier", "Courrier administratif"],
  ["convocation", "Convocation"],
  ["annonce", "Annonce universitaire"],
  ["reformuler", "Reformuler un texte"],
  ["resumer", "Résumer un texte"],
  ["reponse", "Réponse à une demande"],
];

export default function AdminAssistant() {
  const toast = useToast();
  const [task, setTask] = useState("courrier");
  const [instructions, setInstructions] = useState("");
  const [result, setResult] = useState("");
  const [via, setVia] = useState(false);
  const [loading, setLoading] = useState(false);

  async function run() {
    if (!instructions.trim()) return;
    setLoading(true); setResult("");
    try {
      const { data } = await api.post("/ia/assistant/", { task, instructions });
      setResult(data.result); setVia(data.via_openai);
    } catch { toast.error("Génération impossible."); }
    finally { setLoading(false); }
  }

  return (
    <div>
      <PageHeader title="Assistant administratif IA" subtitle="Rédaction, reformulation et synthèse assistées" />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <label className="label">Type de tâche</label>
          <select className="select mb-3" value={task} onChange={(e) => setTask(e.target.value)}>
            {TASKS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
          </select>
          <label className="label">Éléments / texte à traiter</label>
          <textarea className="textarea" rows={10} value={instructions} onChange={(e) => setInstructions(e.target.value)}
            placeholder="Décrivez l'objet du courrier, ou collez le texte à reformuler / résumer..." />
          <button className="btn-primary mt-3 w-full" onClick={run} disabled={loading}>
            {loading ? <Spinner className="h-4 w-4" /> : <Wand2 className="h-4 w-4" />} Générer
          </button>
        </div>

        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-semibold text-slate-700">Résultat</h3>
            {result && <span className={`badge ${via ? "bg-sky-100 text-sky-700" : "bg-slate-100 text-slate-600"}`}>{via ? "OpenAI" : "moteur local"}</span>}
          </div>
          {result ? (
            <>
              <div className="whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm leading-relaxed">{result}</div>
              <button className="btn-light btn-sm mt-2" onClick={() => { navigator.clipboard.writeText(result); toast.success("Copié."); }}>
                <Copy className="h-4 w-4" /> Copier
              </button>
              <p className="mt-3 flex items-center gap-1 rounded-lg bg-amber-50 p-2 text-xs text-amber-700">
                <AlertTriangle className="h-3.5 w-3.5" /> À vérifier et valider par un responsable avant diffusion.
              </p>
            </>
          ) : (
            <div className="py-16 text-center text-sm text-slate-400">Le texte généré apparaîtra ici.</div>
          )}
        </div>
      </div>
    </div>
  );
}
