import CrudResource from "../components/CrudResource";

export default function Niveaux() {
  return (
    <CrudResource
      endpoint="/niveaux/"
      title="Niveaux"
      subtitle="L1, L2, L3, M1, M2..."
      canWrite
      searchable={false}
      columns={[
        { key: "code", label: "Code", render: (r) => <span className="font-semibold">{r.code}</span> },
        { key: "libelle", label: "Libellé" },
        { key: "ordre", label: "Ordre" },
        { key: "nb_etudiants", label: "Étudiants", render: (r) => <span className="chip">{r.nb_etudiants}</span> },
      ]}
      fields={[
        { name: "code", label: "Code", required: true, placeholder: "L1" },
        { name: "libelle", label: "Libellé", required: true, placeholder: "Licence 1" },
        { name: "ordre", label: "Ordre", type: "number" },
      ]}
      defaultValues={{ ordre: 1 }}
    />
  );
}
