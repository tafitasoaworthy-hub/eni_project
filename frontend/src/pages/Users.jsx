import { useState } from "react";
import api from "../api/client";
import CrudResource from "../components/CrudResource";
import { useRefData } from "../data/RefDataContext";
import { Modal, Field, useToast } from "../components/ui";
import { Power, KeyRound } from "lucide-react";

export default function Users() {
  const { enums } = useRefData();
  const toast = useToast();
  const [pwdFor, setPwdFor] = useState(null);
  const [newPwd, setNewPwd] = useState("");

  async function toggle(row, refresh) {
    try {
      await api.post(`/users/${row.id}/toggle_active/`);
      toast.success("Statut du compte modifié."); refresh();
    } catch (e) { toast.error(e.response?.data?.detail || "Action impossible."); }
  }
  async function resetPwd() {
    try {
      await api.post(`/users/${pwdFor.id}/reset_password/`, { new_password: newPwd });
      toast.success("Mot de passe réinitialisé."); setPwdFor(null); setNewPwd("");
    } catch (e) { toast.error(e.response?.data?.detail || "Erreur."); }
  }

  return (
    <>
      <CrudResource
        endpoint="/users/"
        title="Utilisateurs"
        canWrite
        searchPlaceholder="Nom, email..."
        filters={[{ name: "role", label: "Tous les rôles", options: enums.roles || [] }]}
        columns={[
          { key: "full_name", label: "Utilisateur", render: (r) => <div><div className="font-medium">{r.full_name}</div><div className="text-xs text-slate-400">{r.username}</div></div> },
          { key: "role_display", label: "Rôle", render: (r) => <span className="chip">{r.role_display}</span> },
          { key: "email", label: "Email", render: (r) => r.email || "—" },
          { key: "is_active", label: "Statut", render: (r) => r.is_active ? <span className="badge bg-emerald-100 text-emerald-700">Actif</span> : <span className="badge bg-slate-200 text-slate-600">Désactivé</span> },
        ]}
        rowActions={(row, refresh) => (
          <>
            <button className="btn-ghost btn-sm" title="Mot de passe" onClick={() => setPwdFor(row)}><KeyRound className="h-4 w-4" /></button>
            <button className="btn-ghost btn-sm" title="Activer/Désactiver" onClick={() => toggle(row, refresh)}><Power className="h-4 w-4" /></button>
          </>
        )}
        fields={[
          { name: "username", label: "Nom d'utilisateur", required: true },
          { name: "email", label: "Email", type: "email" },
          { name: "first_name", label: "Prénom" },
          { name: "last_name", label: "Nom" },
          { name: "role", label: "Rôle", type: "select", options: enums.roles || [], required: true },
          { name: "phone", label: "Téléphone" },
          { name: "password", label: "Mot de passe (laisser vide pour aléatoire)", type: "password", full: true },
          { name: "is_active", label: "Compte actif", type: "checkbox", checkboxLabel: "Activé", full: true },
        ]}
        defaultValues={{ role: "SCOLARITE", is_active: true }}
      />

      <Modal open={!!pwdFor} onClose={() => setPwdFor(null)} title={`Réinitialiser le mot de passe — ${pwdFor?.username || ""}`} size="sm">
        <Field label="Nouveau mot de passe">
          <input type="password" className="input" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} />
        </Field>
        <div className="mt-4 flex justify-end gap-2">
          <button className="btn-light" onClick={() => setPwdFor(null)}>Annuler</button>
          <button className="btn-primary" onClick={resetPwd}>Réinitialiser</button>
        </div>
      </Modal>
    </>
  );
}
