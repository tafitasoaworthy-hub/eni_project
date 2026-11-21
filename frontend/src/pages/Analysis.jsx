import { useState } from "react";
import api from "../api/client";
import { PageHeader, Spinner } from "../components/ui";
import { LineChart, Lightbulb } from "lucide-react";

export default function Analysis() {
  const [focus, setFocus] = useState("");
  const [result, setResult] = useState("");
  const [via, setVia] = useState(false);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true); setResult("");
    try {
      const { data } = await api.post("/ia/analyse/", { focus });
      setResult(data.result); setVia(data.via_openai);
    } catch { setResult("Analyse impossible pour le moment."); }
    finally { setLoading(false); }
  }

  return (
    <div>
      <PageHeader title="Analyse intelligente des données" subtitle="Synthèse des effectifs et tendances en langage naturel" />
      <div className="card mb-4 flex flex-wrap items-end gap-2 p-4">
        <div className="flex-1 min-w-[240px]">
          <label className="label">Axe d'analyse (optionnel)</label>
          <input className="input" value={focus} onChange={(e) => setFocus(e.target.value)}
            placeholder="Ex : comparer les effectifs entre filières, tendances des inscriptions..." />
        </div>
        <button className="btn-primary" onClick={run} disabled={loading}>
          {loading ? <Spinner className="h-4 w-4" /> : <LineChart className="h-4 w-4" />} Analyser
        </button>
      </div>

      {result ? (
        <div className="card p-5">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="flex items-center gap-2 font-semibold text-slate-700"><Lightbulb className="h-5 w-5 text-brand-600" /> Synthèse</h3>
            <span className={`badge ${via ? "bg-sky-100 text-sky-700" : "bg-slate-100 text-slate-600"}`}>{via ? "OpenAI" : "moteur local"}</span>
          </div>
          <div className="whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm leading-relaxed">{result}</div>
        </div>
      ) : (
        <div className="card py-16 text-center text-sm text-slate-400">
          Lancez une analyse pour obtenir une synthèse des effectifs, filières et tendances d'inscription.
        </div>
      )}
    </div>
  );
}
