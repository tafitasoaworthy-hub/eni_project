import CrudResource from "../components/CrudResource";
import { StatusBadge } from "../components/ui";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";

export default function Students() {
  const { roles } = useAuth();
  const { filieres, niveaux, enums } = useRefData();
  const opt = (arr, l = "nom", v = "id") => arr.map((x) => ({ value: x[v], label: x[l] }));

  return (
    <CrudResource
      endpoint="/etudiants/"
      title="Étudiants"
      canWrite={roles.isStaff}
      canDelete={roles.isAdmin}
      archivable
      searchPlaceholder="Nom, matricule, email..."
      rowLink={(r) => `/etudiants/${r.id}`}
      filters={[
        { name: "filiere", label: "Toutes filières", options: opt(filieres) },
        { name: "niveau", label: "Niveau", options: niveaux.map((n) => ({ value: n.id, label: n.code })) },
        { name: "statut", label: "Statut", options: (enums.student_status || []) },
      ]}
      columns={[
        { key: "matricule", label: "Matricule", render: (r) => <span className="font-semibold text-slate-700">{r.matricule}</span> },
        { key: "full_name", label: "Nom complet", render: (r) => <div><div className="font-medium">{r.full_name}</div><div className="text-xs text-slate-400">{r.email}</div></div> },
        { key: "filiere_nom", label: "Filière" },
        { key: "niveau_code", label: "Niveau", render: (r) => <span className="chip">{r.niveau_code || "—"}</span> },
        { key: "statut", label: "Statut", render: (r) => <StatusBadge value={r.statut} label={r.statut_display} /> },
      ]}
      fields={[
        { name: "nom", label: "Nom", required: true },
        { name: "prenom", label: "Prénom", required: true },
        { name: "genre", label: "Genre", type: "select", options: enums.genres || [] },
        { name: "date_naissance", label: "Date de naissance", type: "date" },
        { name: "lieu_naissance", label: "Lieu de naissance" },
        { name: "nationalite", label: "Nationalité" },
        { name: "email", label: "Email", type: "email" },
        { name: "telephone", label: "Téléphone" },
        { name: "adresse", label: "Adresse", full: true },
        { name: "filiere", label: "Filière", type: "select", options: opt(filieres) },
        { name: "niveau", label: "Niveau", type: "select", options: niveaux.map((n) => ({ value: n.id, label: n.code })) },
        { name: "statut", label: "Statut", type: "select", options: enums.student_status || [] },
      ]}
      defaultValues={{ genre: "M", statut: "ACTIF" }}
    />
  );
}
