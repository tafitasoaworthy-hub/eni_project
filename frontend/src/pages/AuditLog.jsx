import { useList } from "../hooks/useList";
import { useRefData } from "../data/RefDataContext";
import { PageHeader, Loading, Empty, Pagination } from "../components/ui";
import { Search } from "lucide-react";

export default function AuditLog() {
  const { enums } = useRefData();
  const { results, count, loading, params, setParam } = useList("/journal/");

  return (
    <div>
      <PageHeader title="Journal des actions" subtitle={`${count} entrée(s)`} />
      <div className="card mb-4 flex flex-wrap gap-2 p-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input className="input pl-9" placeholder="Rechercher..." onChange={(e) => setParam("search", e.target.value)} />
        </div>
        <select className="select w-auto" value={params.action || ""} onChange={(e) => setParam("action", e.target.value)}>
          <option value="">Toutes les actions</option>
          {(enums.audit_actions || []).map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
        </select>
      </div>
      <div className="card overflow-hidden">
        {loading ? <Loading /> : results.length === 0 ? <Empty /> : (
          <div className="overflow-x-auto"><table className="w-full text-sm">
            <thead><tr className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase text-slate-500">
              <th className="px-4 py-3">Date</th><th className="px-4 py-3">Utilisateur</th><th className="px-4 py-3">Action</th><th className="px-4 py-3">Détail</th><th className="px-4 py-3">IP</th>
            </tr></thead>
            <tbody>
              {results.map((l) => (
                <tr key={l.id} className="border-b border-slate-50">
                  <td className="whitespace-nowrap px-4 py-2.5 text-xs">{new Date(l.created_at).toLocaleString("fr-FR")}</td>
                  <td className="px-4 py-2.5">{l.user_name}</td>
                  <td className="px-4 py-2.5"><span className="chip">{l.action_display}</span></td>
                  <td className="px-4 py-2.5 text-slate-600">{l.message}</td>
                  <td className="px-4 py-2.5 text-xs text-slate-400">{l.ip_address || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        )}
      </div>
      <Pagination count={count} pageSize={12} page={params.page} onChange={(p) => setParam("page", p)} />
    </div>
  );
}
