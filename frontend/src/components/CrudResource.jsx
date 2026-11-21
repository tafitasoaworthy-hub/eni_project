import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useList } from "../hooks/useList";
import {
  PageHeader, Modal, ConfirmDialog, Field, Loading, Empty, Pagination, useToast,
} from "./ui";
import { Plus, Search, Pencil, Trash2, Archive, Eye } from "lucide-react";

/**
 * Generic list + create/edit/delete/archive resource.
 */
export default function CrudResource({
  endpoint,
  title,
  subtitle,
  canWrite = false,
  canDelete = false,
  archivable = false,
  searchable = true,
  searchPlaceholder = "Rechercher...",
  filters = [],
  columns,
  fields,
  defaultValues = {},
  rowLink,
  extraActions,
  rowActions,
}) {
  const toast = useToast();
  const nav = useNavigate();
  const [showArchived, setShowArchived] = useState(false);
  const initial = archivable ? { archived: "false" } : {};
  const { results, count, loading, params, setParam, refresh } = useList(endpoint, initial);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({});
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [confirm, setConfirm] = useState(null);

  function openCreate() {
    setEditing(null);
    setForm({ ...defaultValues });
    setErrors({});
    setModalOpen(true);
  }
  function openEdit(row) {
    setEditing(row);
    const f = {};
    fields.forEach((fl) => {
      f[fl.name] = row[fl.name] ?? "";
    });
    setForm(f);
    setErrors({});
    setModalOpen(true);
  }

  async function save(e) {
    e.preventDefault();
    setSaving(true);
    setErrors({});
    try {
      if (editing) await api.put(`${endpoint}${editing.id}/`, form);
      else await api.post(endpoint, form);
      toast.success(editing ? "Modifié avec succès." : "Créé avec succès.");
      setModalOpen(false);
      refresh();
    } catch (err) {
      if (err.response?.data && typeof err.response.data === "object") setErrors(err.response.data);
      toast.error("Erreur lors de l'enregistrement. Vérifiez les champs.");
    } finally {
      setSaving(false);
    }
  }

  async function doArchive(row) {
    try {
      await api.post(`${endpoint}${row.id}/toggle_archive/`);
      toast.success(row.archived ? "Restauré." : "Archivé.");
      refresh();
    } catch {
      toast.error("Opération impossible.");
    }
    setConfirm(null);
  }
  async function doDelete(row) {
    try {
      await api.delete(`${endpoint}${row.id}/`);
      toast.success("Supprimé.");
      refresh();
    } catch {
      toast.error("Suppression impossible (données liées ?).");
    }
    setConfirm(null);
  }

  function toggleArchivedView() {
    const next = !showArchived;
    setShowArchived(next);
    setParam("archived", next ? "true" : "false");
  }

  return (
    <div>
      <PageHeader
        title={title}
        subtitle={subtitle || `${count} élément(s)`}
        actions={
          <div className="flex gap-2">
            {archivable && (
              <button className="btn-light" onClick={toggleArchivedView}>
                <Archive className="h-4 w-4" /> {showArchived ? "Actifs" : "Archives"}
              </button>
            )}
            {extraActions}
            {canWrite && (
              <button className="btn-primary" onClick={openCreate}>
                <Plus className="h-4 w-4" /> Ajouter
              </button>
            )}
          </div>
        }
      />

      {(searchable || filters.length > 0) && (
        <div className="card mb-4 flex flex-wrap items-center gap-2 p-3">
          {searchable && (
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                className="input pl-9"
                placeholder={searchPlaceholder}
                defaultValue={params.search || ""}
                onChange={(e) => setParam("search", e.target.value)}
              />
            </div>
          )}
          {filters.map((f) => (
            <select
              key={f.name}
              className="select w-auto min-w-[150px]"
              value={params[f.name] || ""}
              onChange={(e) => setParam(f.name, e.target.value)}
            >
              <option value="">{f.label}</option>
              {f.options.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          ))}
        </div>
      )}

      <div className="card overflow-hidden">
        {loading ? (
          <Loading />
        ) : results.length === 0 ? (
          <Empty />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  {columns.map((c) => (
                    <th key={c.key} className="px-4 py-3 font-semibold">{c.label}</th>
                  ))}
                  <th className="px-4 py-3 text-right font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {results.map((row) => (
                  <tr key={row.id} className="border-b border-slate-50 hover:bg-slate-50/60">
                    {columns.map((c) => (
                      <td key={c.key} className="px-4 py-3 align-middle">
                        {c.render ? c.render(row) : row[c.key]}
                      </td>
                    ))}
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        {rowActions && rowActions(row, refresh)}
                        {rowLink && (
                          <button className="btn-ghost btn-sm" title="Voir" onClick={() => nav(rowLink(row))}>
                            <Eye className="h-4 w-4" />
                          </button>
                        )}
                        {canWrite && (
                          <button className="btn-ghost btn-sm" title="Modifier" onClick={() => openEdit(row)}>
                            <Pencil className="h-4 w-4" />
                          </button>
                        )}
                        {canWrite && archivable && (
                          <button className="btn-ghost btn-sm" title="Archiver"
                            onClick={() => setConfirm({ type: "archive", row })}>
                            <Archive className="h-4 w-4" />
                          </button>
                        )}
                        {canDelete && (
                          <button className="btn-ghost btn-sm text-red-500" title="Supprimer"
                            onClick={() => setConfirm({ type: "delete", row })}>
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <Pagination count={count} page={params.page} onChange={(p) => setParam("page", p)} />

      {/* Form modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editing ? "Modifier" : "Ajouter"}>
        <form onSubmit={save}>
          <div className="grid gap-3 sm:grid-cols-2">
            {fields.map((fl) => (
              <Field
                key={fl.name}
                label={fl.label}
                error={errors[fl.name]?.toString()}
                className={fl.full ? "sm:col-span-2" : ""}
              >
                <FieldInput field={fl} value={form[fl.name]} onChange={(v) => setForm((s) => ({ ...s, [fl.name]: v }))} />
              </Field>
            ))}
          </div>
          <div className="mt-5 flex justify-end gap-2">
            <button type="button" className="btn-light" onClick={() => setModalOpen(false)}>Annuler</button>
            <button className="btn-primary" disabled={saving}>{saving ? "Enregistrement..." : "Enregistrer"}</button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!confirm}
        onClose={() => setConfirm(null)}
        onConfirm={() => (confirm.type === "delete" ? doDelete(confirm.row) : doArchive(confirm.row))}
        danger={confirm?.type === "delete"}
        title={confirm?.type === "delete" ? "Supprimer définitivement ?" : (confirm?.row?.archived ? "Restaurer ?" : "Archiver ?")}
        message={confirm?.type === "delete" ? "Cette action est irréversible." : "Vous pourrez le retrouver dans les archives."}
      />
    </div>
  );
}

function FieldInput({ field, value, onChange }) {
  if (field.type === "checkbox") {
    return (
      <label className="flex items-center gap-2 text-sm text-slate-600">
        <input type="checkbox" checked={!!value} onChange={(e) => onChange(e.target.checked)} /> {field.checkboxLabel || "Oui"}
      </label>
    );
  }
  if (field.type === "select") {
    return (
      <select className="select" value={value ?? ""} onChange={(e) => onChange(e.target.value)} required={field.required}>
        <option value="">—</option>
        {field.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    );
  }
  if (field.type === "textarea") {
    return <textarea className="textarea" rows={field.rows || 3} value={value ?? ""} onChange={(e) => onChange(e.target.value)} />;
  }
  return (
    <input
      className="input"
      type={field.type || "text"}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      required={field.required}
      placeholder={field.placeholder}
    />
  );
}
