import CrudResource from "../components/CrudResource";
import { useRefData } from "../data/RefDataContext";

export default function Templates() {
  const { enums } = useRefData();
  return (
    <CrudResource
      endpoint="/modeles-documents/"
      title="Modèles de documents"
      subtitle="Variables : {{ nom }}, {{ prenom }}, {{ matricule }}, {{ filiere }}, {{ niveau }}, {{ annee }}, {{ date }}, {{ universite }}"
      canWrite
      searchable={false}
      columns={[
        { key: "nom", label: "Nom", render: (r) => <span className="font-medium">{r.nom}</span> },
        { key: "type_display", label: "Type", render: (r) => <span className="chip">{r.type_display}</span> },
        { key: "corps", label: "Aperçu", render: (r) => <span className="text-slate-500">{r.corps.slice(0, 80)}…</span> },
      ]}
      fields={[
        { name: "nom", label: "Nom du modèle", required: true, full: true },
        { name: "type_document", label: "Type", type: "select", options: enums.document_types || [], required: true, full: true },
        { name: "corps", label: "Corps du modèle", type: "textarea", rows: 10, full: true, required: true },
      ]}
      defaultValues={{ type_document: "ATTESTATION" }}
    />
  );
}
