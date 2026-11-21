import CrudResource from "../components/CrudResource";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";

export default function Filieres() {
  const { roles } = useAuth();
  const { departements } = useRefData();
  const depOpts = departements.map((d) => ({ value: d.id, label: d.nom }));
  return (
    <CrudResource
      endpoint="/filieres/"
      title="Filières"
      canWrite={roles.isAdmin}
      archivable
      searchPlaceholder="Nom ou code..."
      filters={[{ name: "departement", label: "Tous départements", options: depOpts }]}
      columns={[
        { key: "code", label: "Code", render: (r) => <span className="chip">{r.code}</span> },
        { key: "nom", label: "Filière", render: (r) => <span className="font-medium">{r.nom}</span> },
        { key: "departement_nom", label: "Département" },
        { key: "parcours", label: "Parcours", render: (r) => r.parcours || "—" },
        { key: "nb_etudiants", label: "Étudiants", render: (r) => <span className="chip">{r.nb_etudiants}</span> },
      ]}
      fields={[
        { name: "code", label: "Code", required: true },
        { name: "nom", label: "Nom", required: true },
        { name: "departement", label: "Département", type: "select", options: depOpts, required: true },
        { name: "parcours", label: "Parcours" },
        { name: "description", label: "Description", type: "textarea", full: true },
      ]}
    />
  );
}
