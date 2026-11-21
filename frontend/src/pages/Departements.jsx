import CrudResource from "../components/CrudResource";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";

export default function Departements() {
  const { roles } = useAuth();
  const { enseignants } = useRefData();
  return (
    <CrudResource
      endpoint="/departements/"
      title="Départements"
      canWrite={roles.isAdmin}
      archivable
      searchPlaceholder="Nom ou code..."
      columns={[
        { key: "code", label: "Code", render: (r) => <span className="chip">{r.code}</span> },
        { key: "nom", label: "Département", render: (r) => <span className="font-medium">{r.nom}</span> },
        { key: "responsable_nom", label: "Responsable", render: (r) => r.responsable_nom || "—" },
        { key: "nb_filieres", label: "Filières" },
        { key: "nb_enseignants", label: "Enseignants" },
      ]}
      fields={[
        { name: "code", label: "Code", required: true },
        { name: "nom", label: "Nom", required: true },
        { name: "responsable", label: "Responsable", type: "select", options: enseignants.map((t) => ({ value: t.id, label: t.full_name })) },
        { name: "description", label: "Description", type: "textarea", full: true },
      ]}
    />
  );
}
