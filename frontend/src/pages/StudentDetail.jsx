import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import api from "../api/client";
import { Loading, StatusBadge } from "../components/ui";
import { openDocumentPdf } from "../api/pdf";
import {
  ArrowLeft, Pencil, FileSignature, Mail, Phone, MapPin, Flag, Cake,
  FolderTree, Layers, FileText,
} from "lucide-react";

export default function StudentDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [student, setStudent] = useState(null);
  const [enrollments, setEnrollments] = useState([]);
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    api.get(`/etudiants/${id}/`).then(({ data }) => setStudent(data));
    api.get(`/etudiants/${id}/enrollments/`).then(({ data }) => setEnrollments(data));
    api.get(`/documents-generes/`, { params: { student: id } }).then(({ data }) => setDocs(data.results || data));
  }, [id]);

  if (!student) return <Loading />;
  const initials = `${student.prenom?.[0] || ""}${student.nom?.[0] || ""}`.toUpperCase();

  return (
    <div>
      <button className="btn-ghost btn-sm mb-3" onClick={() => nav("/etudiants")}>
        <ArrowLeft className="h-4 w-4" /> Retour
      </button>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card p-6 text-center">
          <div className="mx-auto mb-3 flex h-24 w-24 items-center justify-center rounded-2xl bg-brand-600 text-3xl font-bold text-white">{initials}</div>
          <h2 className="text-lg font-bold">{student.full_name}</h2>
          <div className="text-sm text-slate-400">{student.matricule}</div>
          <div className="mt-2"><StatusBadge value={student.statut} label={student.statut_display} /></div>
          <div className="mt-4 space-y-1.5 text-left text-sm text-slate-600">
            <p className="flex items-center gap-2"><FolderTree className="h-4 w-4 text-slate-400" /> {student.filiere_nom || "—"}</p>
            <p className="flex items-center gap-2"><Layers className="h-4 w-4 text-slate-400" /> {student.niveau_code || "—"}</p>
            <p className="flex items-center gap-2"><Cake className="h-4 w-4 text-slate-400" /> {student.date_naissance || "—"} {student.lieu_naissance && `à ${student.lieu_naissance}`}</p>
            <p className="flex items-center gap-2"><Flag className="h-4 w-4 text-slate-400" /> {student.nationalite || "—"}</p>
            <p className="flex items-center gap-2"><Mail className="h-4 w-4 text-slate-400" /> {student.email || "—"}</p>
            <p className="flex items-center gap-2"><Phone className="h-4 w-4 text-slate-400" /> {student.telephone || "—"}</p>
            <p className="flex items-center gap-2"><MapPin className="h-4 w-4 text-slate-400" /> {student.adresse || "—"}</p>
          </div>
        </div>

        <div className="space-y-4 lg:col-span-2">
          <div className="card p-5">
            <h3 className="mb-3 font-semibold text-slate-700">Historique des inscriptions</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-slate-100 text-left text-xs uppercase text-slate-500">
                  <th className="py-2">Année</th><th>Filière</th><th>Niveau</th><th>Type</th><th>Statut</th>
                </tr></thead>
                <tbody>
                  {enrollments.map((e) => (
                    <tr key={e.id} className="border-b border-slate-50">
                      <td className="py-2">{e.annee_libelle}</td><td>{e.filiere_nom}</td>
                      <td>{e.niveau_code}</td><td>{e.type_display}</td>
                      <td><StatusBadge value={e.statut} label={e.statut_display} /></td>
                    </tr>
                  ))}
                  {enrollments.length === 0 && <tr><td colSpan={5} className="py-4 text-center text-slate-400">Aucune inscription.</td></tr>}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card p-5">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-semibold text-slate-700">Documents administratifs</h3>
              <Link to={`/documents/generer/${id}`} className="btn-outline btn-sm"><FileSignature className="h-4 w-4" /> Générer un document</Link>
            </div>
            <ul className="divide-y divide-slate-50">
              {docs.map((d) => (
                <li key={d.id} className="flex items-center justify-between py-2 text-sm">
                  <span className="flex items-center gap-2"><FileText className="h-4 w-4 text-slate-400" /> {d.titre}
                    {d.valide && <span className="badge bg-emerald-100 text-emerald-700">validé</span>}
                    {d.genere_par_ia && <span className="badge bg-sky-100 text-sky-700">IA</span>}
                  </span>
                  <button className="btn-ghost btn-sm" onClick={() => openDocumentPdf(d.id)}>PDF</button>
                </li>
              ))}
              {docs.length === 0 && <li className="py-3 text-slate-400">Aucun document généré.</li>}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
