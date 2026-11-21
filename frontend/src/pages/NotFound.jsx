import { Link } from "react-router-dom";
import { Compass } from "lucide-react";

export default function NotFound() {
  return (
    <div className="card p-16 text-center">
      <Compass className="mx-auto mb-4 h-12 w-12 text-slate-300" />
      <h2 className="text-xl font-bold text-slate-700">404 — Page introuvable</h2>
      <p className="mb-5 text-slate-400">La page demandée n'existe pas.</p>
      <Link to="/" className="btn-primary mx-auto w-fit">Retour au tableau de bord</Link>
    </div>
  );
}
