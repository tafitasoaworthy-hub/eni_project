import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { Spinner } from "../components/ui";
import { LogIn } from "lucide-react";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      nav("/");
    } catch (err) {
      setError(
        err.response?.status === 401
          ? "Nom d'utilisateur ou mot de passe incorrect."
          : "Connexion impossible. Vérifiez que le serveur est démarré."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-ink to-brand-600 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-soft">
        <div className="mb-6 text-center">
          <img src="/logo.jpg" alt="logo" className="mx-auto mb-3 h-16 w-16 rounded-2xl object-cover" />
          <h1 className="text-xl font-bold text-brand-700">Université ENI</h1>
          <p className="text-sm text-slate-500">Plateforme de Gestion Universitaire</p>
        </div>
        {error && <div className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="label">Nom d'utilisateur</label>
            <input className="input" value={username} onChange={(e) => setU(e.target.value)} autoFocus required />
          </div>
          <div>
            <label className="label">Mot de passe</label>
            <input type="password" className="input" value={password} onChange={(e) => setP(e.target.value)} required />
          </div>
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? <Spinner className="h-4 w-4" /> : <LogIn className="h-4 w-4" />} Se connecter
          </button>
        </form>
        <div className="mt-6 rounded-lg bg-slate-50 p-3 text-xs text-slate-500">
          <div className="mb-1 font-semibold text-slate-600">Comptes de démonstration</div>
          admin / admin123 · scolarite / scolarite123<br />
          enseignant / enseignant123 · etudiant / etudiant123
        </div>
      </div>
    </div>
  );
}
