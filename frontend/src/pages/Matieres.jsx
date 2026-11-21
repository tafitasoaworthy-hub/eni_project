import CrudResource from "../components/CrudResource";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";

export default function Matieres() {
  const { roles } = useAuth();
  const { filieres, niveaux, enseignants, enums } = useRefData();
  const filOpts = filieres.map((f) => ({ value: f.id, label: f.nom }));
  const nivOpts = niveaux.map((n) => ({ value: n.id, label: n.code }));
  return (
    <CrudResource
      endpoint="/matieres/"
      title="Matières / Modules"
      canWrite={roles.isStaff}
      canDelete={roles.isAdmin}
      archivable
      searchPlaceholder="Nom ou code..."
      filters={[
        { name: "filiere", label: "Toutes filières", options: filOpts },
        { name: "niveau", label: "Niveau", options: nivOpts },
      ]}
      columns={[
        { key: "code", label: "Code", render: (r) => <span className="font-semibold">{r.code}</span> },
        { key: "nom", label: "Matière", render: (r) => <span className="font-medium">{r.nom}</span> },
        { key: "filiere_nom", label: "Filière" },
        { key: "niveau_code", label: "Niveau", render: (r) => <span className="chip">{r.niveau_code || "—"}</span> },
        { key: "enseignant_nom", label: "Enseignant", render: (r) => r.enseignant_nom || "—" },
        { key: "credits", label: "Cr." },
        { key: "coefficient", label: "Coef." },
      ]}
      fields={[
        { name: "code", label: "Code", required: true },
        { name: "nom", label: "Nom", required: true },
        { name: "filiere", label: "Filière", type: "select", options: filOpts, required: true },
        { name: "niveau", label: "Niveau", type: "select", options: nivOpts },
        { name: "enseignant", label: "Enseignant", type: "select", options: enseignants.map((t) => ({ value: t.id, label: t.full_name })) },
        { name: "credits", label: "Crédits", type: "number" },
        { name: "coefficient", label: "Coefficient", type: "number" },
        { name: "semestre", label: "Semestre", type: "select", options: enums.semestres || [] },
        { name: "description", label: "Description", type: "textarea", full: true },
      ]}
      defaultValues={{ credits: 3, coefficient: 1, semestre: "S1" }}
    />
  );
}
