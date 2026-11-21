import CrudResource from "../components/CrudResource";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";

export default function Teachers() {
  const { roles } = useAuth();
  const { departements, enums } = useRefData();

  return (
    <CrudResource
      endpoint="/enseignants/"
      title="Enseignants"
      canWrite={roles.isStaff}
      canDelete={roles.isAdmin}
      archivable
      searchPlaceholder="Nom, matricule, spécialité..."
      filters={[{ name: "departement", label: "Tous départements", options: departements.map((d) => ({ value: d.id, label: d.nom })) }]}
      columns={[
        { key: "matricule", label: "Matricule", render: (r) => <span className="font-semibold">{r.matricule}</span> },
        { key: "full_name", label: "Nom", render: (r) => <span className="font-medium">{r.full_name}</span> },
        { key: "specialite", label: "Spécialité" },
        { key: "grade_display", label: "Grade", render: (r) => <span className="chip">{r.grade_display}</span> },
        { key: "departement_nom", label: "Département" },
      ]}
      fields={[
        { name: "matricule", label: "Matricule", required: true },
        { name: "nom", label: "Nom", required: true },
        { name: "prenom", label: "Prénom", required: true },
        { name: "email", label: "Email", type: "email" },
        { name: "telephone", label: "Téléphone" },
        { name: "specialite", label: "Spécialité" },
        { name: "grade", label: "Grade", type: "select", options: enums.teacher_grades || [] },
        { name: "departement", label: "Département", type: "select", options: departements.map((d) => ({ value: d.id, label: d.nom })) },
      ]}
      defaultValues={{ grade: "ASSISTANT" }}
    />
  );
}
