import { useEffect, useState } from "react";
import api from "../api/client";
import { useRefData } from "../data/RefDataContext";
import { PageHeader, Modal, Field, Loading, useToast, ConfirmDialog } from "../components/ui";
import { Plus, AlertTriangle, Pencil, Trash2 } from "lucide-react";

const JOURS = [[1, "Lundi"], [2, "Mardi"], [3, "Mercredi"], [4, "Jeudi"], [5, "Vendredi"], [6, "Samedi"]];

export default function Schedules() {
  const { filieres, niveaux, annees, enseignants, anneeCourante, enums } = useRefData();
  const toast = useToast();
  const [seances, setSeances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ annee: "", filiere: "", niveau: "", enseignant: "" });
  const [matieres, setMatieres] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({});
  const [editing, setEditing] = useState(null);
  const [confirm, setConfirm] = useState(null);

  function load() {
    setLoading(true);
    const params = { ...filters };
    if (!params.annee && anneeCourante) params.annee = anneeCourante.id;
    api.get("/seances/", { params: { ...params, page_size: 300 } })
      .then(({ data }) => setSeances(data.results || data))
      .finally(() => setLoading(false));
  }
  useEffect(() => { if (anneeCourante !== undefined) load(); }, [filters, anneeCourante]);
  useEffect(() => { api.get("/matieres/", { params: { page_size: 500 } }).then(({ data }) => setMatieres(data.results || data)); }, []);

  const conflicts = seances.filter((s) => s.has_conflict).length;

  function openCreate() { setEditing(null); setForm({ annee: anneeCourante?.id || "", type_seance: "CM", jour: 1 }); setModal(true); }
  function openEdit(s) {
    setEditing(s);
    setForm({ annee: s.annee, filiere: s.filiere, niveau: s.niveau, matiere: s.matiere, enseignant: s.enseignant || "",
      salle: s.salle, jour: s.jour, heure_debut: s.heure_debut, heure_fin: s.heure_fin, type_seance: s.type_seance });
    setModal(true);
  }
  async function save(e) {
    e.preventDefault();
    try {
      if (editing) await api.put(`/seances/${editing.id}/`, form);
      else await api.post("/seances/", form);
      toast.success("Séance enregistrée.");
      setModal(false); load();
    } catch { toast.error("Vérifiez les champs (horaires, matière...)."); }
  }
  async function del(s) { await api.delete(`/seances/${s.id}/`); toast.success("Supprimée."); setConfirm(null); load(); }

  const filOpts = filieres.map((f) => ({ value: f.id, label: f.nom }));
  const nivOpts = niveaux.map((n) => ({ value: n.id, label: n.code }));

  return (
    <div>
      <PageHeader
        title="Emplois du temps"
        subtitle={`${seances.length} séance(s)`}
        actions={<button className="btn-primary" onClick={openCreate}><Plus className="h-4 w-4" /> Nouvelle séance</button>}
      />

      <div className="card mb-4 flex flex-wrap gap-2 p-3">
        <select className="select w-auto" value={filters.annee} onChange={(e) => setFilters((f) => ({ ...f, annee: e.target.value }))}>
          <option value="">Année courante</option>
          {annees.map((a) => <option key={a.id} value={a.id}>{a.libelle}</option>)}
        </select>
        <select className="select w-auto" value={filters.filiere} onChange={(e) => setFilters((f) => ({ ...f, filiere: e.target.value }))}>
          <option value="">Toutes filières</option>
          {filOpts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select className="select w-auto" value={filters.niveau} onChange={(e) => setFilters((f) => ({ ...f, niveau: e.target.value }))}>
          <option value="">Niveau</option>
          {nivOpts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select className="select w-auto" value={filters.enseignant} onChange={(e) => setFilters((f) => ({ ...f, enseignant: e.target.value }))}>
          <option value="">Enseignant</option>
          {enseignants.map((t) => <option key={t.id} value={t.id}>{t.full_name}</option>)}
        </select>
        {conflicts > 0 && (
          <span className="badge bg-red-100 text-red-700"><AlertTriangle className="mr-1 h-3.5 w-3.5" /> {conflicts} conflit(s)</span>
        )}
      </div>

      {loading ? <Loading /> : (
        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
          {JOURS.map(([num, nom]) => (
            <div key={num} className="card p-2">
              <h4 className="mb-2 border-b border-slate-100 pb-1 text-center text-sm font-semibold text-brand-700">{nom}</h4>
              <div className="space-y-2">
                {seances.filter((s) => s.jour === num).sort((a, b) => a.heure_debut.localeCompare(b.heure_debut)).map((s) => (
                  <div key={s.id} className={`group rounded-lg border-l-4 p-2 text-xs ${s.has_conflict ? "border-red-500 bg-red-50" : "border-gold bg-amber-50/60"}`}>
                    <div className="font-semibold">{s.heure_debut?.slice(0, 5)}–{s.heure_fin?.slice(0, 5)}</div>
                    <div className="text-slate-700">{s.matiere_nom}</div>
                    <div className="text-slate-500">{s.type_display} · {s.filiere_nom}/{s.niveau_code}</div>
                    <div className="text-slate-500">{s.enseignant_nom}{s.salle && ` · ${s.salle}`}</div>
                    <div className="mt-1 hidden gap-1 group-hover:flex">
                      <button className="btn-ghost btn-sm !px-1 !py-0.5" onClick={() => openEdit(s)}><Pencil className="h-3 w-3" /></button>
                      <button className="btn-ghost btn-sm !px-1 !py-0.5 text-red-500" onClick={() => setConfirm(s)}><Trash2 className="h-3 w-3" /></button>
                    </div>
                  </div>
                ))}
                {seances.filter((s) => s.jour === num).length === 0 && <div className="py-2 text-center text-xs text-slate-300">—</div>}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modal} onClose={() => setModal(false)} title={editing ? "Modifier la séance" : "Nouvelle séance"}>
        <form onSubmit={save} className="grid gap-3 sm:grid-cols-2">
          <Field label="Année"><select className="select" value={form.annee || ""} onChange={(e) => setForm({ ...form, annee: e.target.value })} required><option value="">—</option>{annees.map((a) => <option key={a.id} value={a.id}>{a.libelle}</option>)}</select></Field>
          <Field label="Type"><select className="select" value={form.type_seance || "CM"} onChange={(e) => setForm({ ...form, type_seance: e.target.value })}>{(enums.seance_types || []).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></Field>
          <Field label="Filière"><select className="select" value={form.filiere || ""} onChange={(e) => setForm({ ...form, filiere: e.target.value })} required><option value="">—</option>{filOpts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></Field>
          <Field label="Niveau"><select className="select" value={form.niveau || ""} onChange={(e) => setForm({ ...form, niveau: e.target.value })} required><option value="">—</option>{nivOpts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}</select></Field>
          <Field label="Matière"><select className="select" value={form.matiere || ""} onChange={(e) => setForm({ ...form, matiere: e.target.value })} required><option value="">—</option>{matieres.map((m) => <option key={m.id} value={m.id}>{m.nom} ({m.code})</option>)}</select></Field>
          <Field label="Enseignant"><select className="select" value={form.enseignant || ""} onChange={(e) => setForm({ ...form, enseignant: e.target.value })}><option value="">—</option>{enseignants.map((t) => <option key={t.id} value={t.id}>{t.full_name}</option>)}</select></Field>
          <Field label="Jour"><select className="select" value={form.jour || 1} onChange={(e) => setForm({ ...form, jour: e.target.value })}>{JOURS.map(([n, l]) => <option key={n} value={n}>{l}</option>)}</select></Field>
          <Field label="Salle"><input className="input" value={form.salle || ""} onChange={(e) => setForm({ ...form, salle: e.target.value })} /></Field>
          <Field label="Heure début"><input type="time" className="input" value={form.heure_debut || ""} onChange={(e) => setForm({ ...form, heure_debut: e.target.value })} required /></Field>
          <Field label="Heure fin"><input type="time" className="input" value={form.heure_fin || ""} onChange={(e) => setForm({ ...form, heure_fin: e.target.value })} required /></Field>
          <div className="col-span-2 mt-2 flex justify-end gap-2">
            <button type="button" className="btn-light" onClick={() => setModal(false)}>Annuler</button>
            <button className="btn-primary">Enregistrer</button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog open={!!confirm} onClose={() => setConfirm(null)} onConfirm={() => del(confirm)} danger
        title="Supprimer la séance ?" message="Cette action est irréversible." />
    </div>
  );
}
