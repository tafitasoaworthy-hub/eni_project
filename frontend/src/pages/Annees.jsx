import CrudResource from "../components/CrudResource";
import api from "../api/client";
import { useRefData } from "../data/RefDataContext";
import { useToast } from "../components/ui";
import { CheckCircle2 } from "lucide-react";

export default function Annees() {
  const { reload } = useRefData();
  const toast = useToast();

  async function setCurrent(row, refresh) {
    await api.post(`/annees/${row.id}/set_current/`);
    toast.success(`« ${row.libelle} » est l'année courante.`);
    refresh();
    reload();
  }

  return (
    <CrudResource
      endpoint="/annees/"
      title="Années universitaires"
      canWrite
      searchable={false}
      columns={[
        { key: "libelle", label: "Libellé", render: (r) => <span className="font-semibold">{r.libelle}</span> },
        { key: "date_debut", label: "Début", render: (r) => r.date_debut || "—" },
        { key: "date_fin", label: "Fin", render: (r) => r.date_fin || "—" },
        { key: "nb_inscriptions", label: "Inscriptions", render: (r) => <span className="chip">{r.nb_inscriptions}</span> },
        { key: "courante", label: "Courante", render: (r) => r.courante ? <span className="badge bg-emerald-100 text-emerald-700">Courante</span> : "—" },
      ]}
      rowActions={(row, refresh) =>
        !row.courante && (
          <button className="btn-ghost btn-sm text-emerald-600" title="Définir comme courante" onClick={() => setCurrent(row, refresh)}>
            <CheckCircle2 className="h-4 w-4" />
          </button>
        )
      }
      fields={[
        { name: "libelle", label: "Libellé", required: true, placeholder: "2024-2025" },
        { name: "date_debut", label: "Date de début", type: "date" },
        { name: "date_fin", label: "Date de fin", type: "date" },
      ]}
    />
  );
}
