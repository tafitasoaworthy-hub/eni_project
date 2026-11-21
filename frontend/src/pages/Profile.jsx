import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { PageHeader, Field, useToast } from "../components/ui";
import { Save, KeyRound } from "lucide-react";

export default function Profile() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const [sp] = useSearchParams();
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", phone: "" });
  const [pwd, setPwd] = useState({ old_password: "", new_password: "" });

  useEffect(() => {
    if (user) setForm({ first_name: user.first_name || "", last_name: user.last_name || "", email: user.email || "", phone: user.phone || "" });
  }, [user]);

  async function saveProfile(e) {
    e.preventDefault();
    try {
      const { data } = await api.patch("/auth/me/", form);
      setUser(data); localStorage.setItem("user", JSON.stringify(data));
      toast.success("Profil mis à jour.");
    } catch { toast.error("Mise à jour impossible."); }
  }
  async function changePwd(e) {
    e.preventDefault();
    try {
      await api.post("/auth/password/", pwd);
      toast.success("Mot de passe modifié."); setPwd({ old_password: "", new_password: "" });
    } catch (err) { toast.error(err.response?.data?.detail || "Erreur."); }
  }

  const initials = (user?.full_name || user?.username || "?").split(" ").map((s) => s[0]).slice(0, 2).join("").toUpperCase();

  return (
    <div>
      <PageHeader title="Mon profil" />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card p-6 text-center">
          <div className="mx-auto mb-3 flex h-24 w-24 items-center justify-center rounded-2xl bg-brand-600 text-3xl font-bold text-white">{initials}</div>
          <h2 className="text-lg font-bold">{user?.full_name}</h2>
          <div className="text-sm text-slate-400">{user?.role_display}</div>
          <div className="mt-2 text-sm text-slate-500">{user?.username}</div>
        </div>

        <div className="space-y-4 lg:col-span-2">
          <form className="card p-5" onSubmit={saveProfile}>
            <h3 className="mb-3 font-semibold text-slate-700">Mes informations</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Prénom"><input className="input" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} /></Field>
              <Field label="Nom"><input className="input" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} /></Field>
              <Field label="Email"><input type="email" className="input" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></Field>
              <Field label="Téléphone"><input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></Field>
            </div>
            <button className="btn-primary mt-4"><Save className="h-4 w-4" /> Enregistrer</button>
          </form>

          <form className="card p-5" onSubmit={changePwd} id="pwd">
            <h3 className="mb-3 flex items-center gap-2 font-semibold text-slate-700"><KeyRound className="h-4 w-4 text-brand-600" /> Changer le mot de passe</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              <Field label="Ancien mot de passe"><input type="password" className="input" value={pwd.old_password} onChange={(e) => setPwd({ ...pwd, old_password: e.target.value })} required /></Field>
              <Field label="Nouveau mot de passe"><input type="password" className="input" value={pwd.new_password} onChange={(e) => setPwd({ ...pwd, new_password: e.target.value })} required /></Field>
            </div>
            <button className="btn-primary mt-4">Mettre à jour</button>
          </form>
        </div>
      </div>
    </div>
  );
}
