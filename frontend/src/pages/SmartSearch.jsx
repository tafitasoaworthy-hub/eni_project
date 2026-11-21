import { useState } from "react";
import api from "../api/client";
import { PageHeader, Spinner } from "../components/ui";
import { Search, Shield } from "lucide-react";

const EXAMPLES = [
  "Combien d'étudiants sont inscrits au total ?",
  "Quels documents sont nécessaires pour une inscription ?",
  "Combien d'enseignants au total ?",
];

export default function SmartSearch() {
  const [q, setQ] = useState("");
  const [res, setRes] = useState(null);
  const [via, setVia] = useState(false);
  const [loading, setLoading] = useState(false);

  async function run(query) {
    const text = (query ?? q).trim();
    if (!text) return;
    setQ(text); setLoading(true); setRes(null);
    try {
      const { data } = await api.get("/ia/recherche/", { params: { q: text } });
      setRes(data.answer); setVia(data.via_openai);
    } catch { setRes("Recherche impossible pour le moment."); }
    finally { setLoading(false); }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <PageHeader title="Recherche intelligente" subtitle="Posez une question en langage naturel" />
      <form className="card flex gap-2 p-3" onSubmit={(e) => { e.preventDefault(); run(); }}>
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-5 w-5 text-slate-400" />
          <input className="input pl-10 text-base" placeholder="Votre question..." value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
        <button className="btn-primary px-6" disabled={loading}>{loading ? <Spinner className="h-4 w-4" /> : <Search className="h-4 w-4" />}</button>
      </form>
      <div className="mt-2 flex flex-wrap gap-2">
        {EXAMPLES.map((e) => <button key={e} className="chip hover:bg-slate-200" onClick={() => run(e)}>{e}</button>)}
      </div>

      {res !== null && (
        <div className="card mt-4 p-5">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-semibold text-slate-700">Réponse</h3>
            <span className={`badge ${via ? "bg-sky-100 text-sky-700" : "bg-slate-100 text-slate-600"}`}>{via ? "OpenAI" : "moteur local"}</span>
          </div>
          <p className="mb-3 text-sm text-slate-400">Question : « {q} »</p>
          <div className="whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm leading-relaxed">{res}</div>
          <p className="mt-2 flex items-center gap-1 text-xs text-slate-400"><Shield className="h-3.5 w-3.5" /> Seules les informations agrégées autorisées sont exposées, sans données personnelles d'autrui.</p>
        </div>
      )}
    </div>
  );
}
