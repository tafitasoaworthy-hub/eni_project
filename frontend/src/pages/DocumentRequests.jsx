import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import CrudResource from "../components/CrudResource";
import { StatusBadge, useToast } from "../components/ui";
import { useRefData } from "../data/RefDataContext";
import { Check, X, FilePlus2 } from "lucide-react";

export default function DocumentRequests() {
  const { enums } = useRefData();
  const toast = useToast();
  const nav = useNavigate();
  const [students, setStudents] = useState([]);

  useEffect(() => {
    api.get("/etudiants/", { params: { page_size: 500 } }).then(({ data }) =>
      setStudents((data.results || data).map((s) => ({ value: s.id, label: `${s.full_name} (${s.matricule})` })))
    );
  }, []);

  async function setStatus(row, refresh, statut) {
    await api.post(`/demandes-documents/${row.id}/set_status/`, { statut });
    toast.success("Statut mis à jour."); refresh();
  }

  return (
    <CrudResource
      endpoint="/demandes-documents/"
      title="Demandes de documents"
      canWrite
      searchable={false}
      filters={[{ name: "statut", label: "Tous les statuts", options: enums.enrollment_status || [] }]}
      columns={[
        { key: "student_nom", label: "Étudiant", render: (r) => <div><div className="font-medium">{r.student_nom}</div><div className="text-xs text-slate-400">{r.student_matricule}</div></div> },
        { key: "type_display", label: "Type" },
        { key: "motif", label: "Motif", render: (r) => r.motif || "—" },
        { key: "created_at", label: "Date", render: (r) => new Date(r.created_at).toLocaleDateString("fr-FR") },
        { key: "statut", label: "Statut", render: (r) => <StatusBadge value={r.statut} label={r.statut_display} /> },
      ]}
      rowActions={(row, refresh) => (
        <>
          <button className="btn-ghost btn-sm text-brand-600" title="Générer le document" onClick={() => nav(`/documents/generer/${row.student}?type=${row.type_document}`)}><FilePlus2 className="h-4 w-4" /></button>
          {row.statut !== "VALIDEE" && <button className="btn-ghost btn-sm text-emerald-600" title="Valider" onClick={() => setStatus(row, refresh, "VALIDEE")}><Check className="h-4 w-4" /></button>}
          {row.statut !== "REFUSEE" && <button className="btn-ghost btn-sm text-red-500" title="Refuser" onClick={() => setStatus(row, refresh, "REFUSEE")}><X className="h-4 w-4" /></button>}
        </>
      )}
      fields={[
        { name: "student", label: "Étudiant", type: "select", options: students, required: true, full: true },
        { name: "type_document", label: "Type de document", type: "select", options: enums.document_types || [], required: true },
        { name: "motif", label: "Motif", full: true },
      ]}
      defaultValues={{ type_document: "ATTESTATION" }}
    />
  );
}
