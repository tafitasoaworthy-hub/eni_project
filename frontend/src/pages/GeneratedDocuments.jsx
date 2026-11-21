import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useList } from "../hooks/useList";
import { openDocumentPdf } from "../api/pdf";
import api from "../api/client";
import { PageHeader, Loading, Empty, Pagination, StatusBadge, useToast } from "../components/ui";
import { FileText, Download, Check, Eye, Archive } from "lucide-react";

export default function GeneratedDocuments() {
  const nav = useNavigate();
  const toast = useToast();
  const [archived, setArchived] = useState(false);
  const { results, count, loading, params, setParam, refresh } = useList("/documents-generes/", { archived: "false" });

  async function validate(d) { await api.post(`/documents-generes/${d.id}/validate/`); toast.success("Document validé."); refresh(); }
  async function toggleArch(d) { await api.post(`/documents-generes/${d.id}/toggle_archive/`); refresh(); }

  return (
    <div>
      <PageHeader title="Documents générés" subtitle={`${count} document(s)`}
        actions={<button className="btn-light" onClick={() => { const n = !archived; setArchived(n); setParam("archived", n ? "true" : "false"); }}>
          <Archive className="h-4 w-4" /> {archived ? "Actifs" : "Archives"}</button>} />
      <div className="card overflow-hidden">
        {loading ? <Loading /> : results.length === 0 ? <Empty /> : (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead><tr className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase text-slate-500">
              <th className="px-4 py-3">Titre</th><th className="px-4 py-3">Étudiant</th><th className="px-4 py-3">Type</th>
              <th className="px-4 py-3">Date</th><th className="px-4 py-3">Statut</th><th className="px-4 py-3 text-right">Actions</th>
            </tr></thead>
            <tbody>
              {results.map((d) => (
                <tr key={d.id} className="border-b border-slate-50 hover:bg-slate-50/60">
                  <td className="px-4 py-3"><span className="flex items-center gap-2 font-medium"><FileText className="h-4 w-4 text-slate-400" />{d.titre}
                    {d.genere_par_ia && <span className="badge bg-sky-100 text-sky-700">IA</span>}</span></td>
                  <td className="px-4 py-3">{d.student_nom}</td>
                  <td className="px-4 py-3">{d.type_display}</td>
                  <td className="px-4 py-3">{new Date(d.created_at).toLocaleDateString("fr-FR")}</td>
                  <td className="px-4 py-3">{d.valide ? <StatusBadge value="VALIDEE" label="Validé" /> : <StatusBadge value="EN_ATTENTE" label="En attente" />}</td>
                  <td className="px-4 py-3"><div className="flex justify-end gap-1">
                    <button className="btn-ghost btn-sm" title="PDF" onClick={() => openDocumentPdf(d.id)}><Download className="h-4 w-4" /></button>
                    {!d.valide && <button className="btn-ghost btn-sm text-emerald-600" title="Valider" onClick={() => validate(d)}><Check className="h-4 w-4" /></button>}
                    <button className="btn-ghost btn-sm" title="Archiver" onClick={() => toggleArch(d)}><Archive className="h-4 w-4" /></button>
                  </div></td>
                </tr>
              ))}
            </tbody>
          </table></div>
        )}
      </div>
      <Pagination count={count} page={params.page} onChange={(p) => setParam("page", p)} />
    </div>
  );
}
