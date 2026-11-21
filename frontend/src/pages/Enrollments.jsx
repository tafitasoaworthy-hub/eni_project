import { useEffect, useState } from "react";
import api from "../api/client";
import CrudResource from "../components/CrudResource";
import { StatusBadge, useToast } from "../components/ui";
import { useRefData } from "../data/RefDataContext";
import { Check, X } from "lucide-react";

export default function Enrollments() {
  const { filieres, niveaux, annees, anneeCourante, enums } = useRefData();
  const toast = useToast();
  const [students, setStudents] = useState([]);

  useEffect(() => {
    api.get("/etudiants/", { params: { page_size: 500 } }).then(({ data }) =>
      setStudents((data.results || data).map((s) => ({ value: s.id, label: `${s.full_name} (${s.matricule})` })))
    );
  }, []);

  const filOpts = filieres.map((f) => ({ value: f.id, label: f.nom }));
  const nivOpts = niveaux.map((n) => ({ value: n.id, label: n.code }));

  async function setStatus(row, refresh, statut) {
    await api.post(`/inscriptions/${row.id}/set_status/`, { statut });
    toast.success("Statut mis à jour.");
    refresh();
  }

  return (
    <CrudResource
      endpoint="/inscriptions/"
      title="Inscriptions"
      canWrite
      searchPlaceholder="Étudiant, matricule..."
      filters={[
        { name: "annee", label: "Année", options: annees.map((a) => ({ value: a.id, label: a.libelle })) },
        { name: "filiere", label: "Filière", options: filOpts },
        { name: "niveau", label: "Niveau", options: nivOpts },
        { name: "statut", label: "Statut", options: enums.enrollment_status || [] },
      ]}
      columns={[
        { key: "student_nom", label: "Étudiant", render: (r) => <div><div className="font-medium">{r.student_nom}</div><div className="text-xs text-slate-400">{r.student_matricule}</div></div> },
        { key: "annee_libelle", label: "Année" },
        { key: "filiere_nom", label: "Filière" },
        { key: "niveau_code", label: "Niveau", render: (r) => <span className="chip">{r.niveau_code}</span> },
        { key: "type_display", label: "Type" },
        { key: "statut", label: "Statut", render: (r) => <StatusBadge value={r.statut} label={r.statut_display} /> },
      ]}
      rowActions={(row, refresh) => (
        <>
          {row.statut !== "VALIDEE" && (
            <button className="btn-ghost btn-sm text-emerald-600" title="Valider" onClick={() => setStatus(row, refresh, "VALIDEE")}><Check className="h-4 w-4" /></button>
          )}
          {row.statut !== "REFUSEE" && (
            <button className="btn-ghost btn-sm text-red-500" title="Refuser" onClick={() => setStatus(row, refresh, "REFUSEE")}><X className="h-4 w-4" /></button>
          )}
        </>
      )}
      fields={[
        { name: "student", label: "Étudiant", type: "select", options: students, required: true, full: true },
        { name: "annee", label: "Année universitaire", type: "select", options: annees.map((a) => ({ value: a.id, label: a.libelle })), required: true },
        { name: "type_inscription", label: "Type", type: "select", options: enums.enrollment_types || [] },
        { name: "filiere", label: "Filière", type: "select", options: filOpts, required: true },
        { name: "niveau", label: "Niveau", type: "select", options: nivOpts, required: true },
        { name: "statut", label: "Statut", type: "select", options: enums.enrollment_status || [] },
        { name: "observation", label: "Observation", type: "textarea", full: true },
      ]}
      defaultValues={{ type_inscription: "NOUVELLE", statut: "EN_ATTENTE", annee: anneeCourante?.id || "" }}
    />
  );
}
