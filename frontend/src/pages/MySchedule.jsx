import { useEffect, useState } from "react";
import api from "../api/client";
import { Loading, PageHeader, Empty } from "../components/ui";

const JOURS = [[1, "Lundi"], [2, "Mardi"], [3, "Mercredi"], [4, "Jeudi"], [5, "Vendredi"], [6, "Samedi"]];

export default function MySchedule() {
  const [seances, setSeances] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/mon-emploi-du-temps/").then(({ data }) => setSeances(data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;

  return (
    <div>
      <PageHeader title="Mon emploi du temps" subtitle={`${seances.length} séance(s)`} />
      {seances.length === 0 ? (
        <div className="card"><Empty message="Aucune séance programmée pour le moment." /></div>
      ) : (
        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {JOURS.map(([num, nom]) => (
            <div key={num} className="card p-2">
              <h4 className="mb-2 border-b border-slate-100 pb-1 text-center text-sm font-semibold text-brand-700">{nom}</h4>
              <div className="space-y-2">
                {seances.filter((s) => s.jour === num).sort((a, b) => a.heure_debut.localeCompare(b.heure_debut)).map((s) => (
                  <div key={s.id} className="rounded-lg border-l-4 border-gold bg-amber-50/60 p-2 text-xs">
                    <div className="font-semibold">{s.heure_debut?.slice(0, 5)}–{s.heure_fin?.slice(0, 5)}</div>
                    <div className="text-slate-700">{s.matiere_nom}</div>
                    <div className="text-slate-500">{s.type_display} · {s.filiere_nom}/{s.niveau_code}</div>
                    <div className="text-slate-500">{s.enseignant_nom}{s.salle && ` · ${s.salle}`}</div>
                  </div>
                ))}
                {seances.filter((s) => s.jour === num).length === 0 && <div className="py-2 text-center text-xs text-slate-300">—</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
