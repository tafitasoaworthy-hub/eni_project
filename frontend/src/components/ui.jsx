import { createContext, useContext, useState, useCallback } from "react";
import { X, Loader2, CheckCircle2, AlertCircle, Info } from "lucide-react";

/* ---------------- Spinner ---------------- */
export function Spinner({ className = "" }) {
  return <Loader2 className={`animate-spin ${className}`} />;
}

export function Loading({ label = "Chargement..." }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-slate-400">
      <Spinner className="h-5 w-5" /> {label}
    </div>
  );
}

/* ---------------- Badge ---------------- */
const STATUS_STYLES = {
  VALIDEE: "bg-emerald-100 text-emerald-700",
  EN_ATTENTE: "bg-amber-100 text-amber-700",
  REFUSEE: "bg-red-100 text-red-700",
  ACTIF: "bg-emerald-100 text-emerald-700",
  DIPLOME: "bg-sky-100 text-sky-700",
  SUSPENDU: "bg-amber-100 text-amber-700",
  ABANDON: "bg-slate-200 text-slate-600",
};
export function StatusBadge({ value, label }) {
  const cls = STATUS_STYLES[value] || "bg-slate-100 text-slate-600";
  return <span className={`badge ${cls}`}>{label || value}</span>;
}

/* ---------------- Modal ---------------- */
export function Modal({ open, onClose, title, children, size = "lg" }) {
  if (!open) return null;
  const width = { sm: "max-w-md", lg: "max-w-2xl", xl: "max-w-4xl" }[size];
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 pt-10">
      <div className={`w-full ${width} rounded-xl bg-white shadow-soft`}>
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <h3 className="font-semibold text-slate-800">{title}</h3>
          <button onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-slate-100">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="px-5 py-4">{children}</div>
      </div>
    </div>
  );
}

/* ---------------- Confirm ---------------- */
export function ConfirmDialog({ open, onClose, onConfirm, title, message, danger }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 text-center shadow-soft">
        <AlertCircle className={`mx-auto mb-3 h-10 w-10 ${danger ? "text-red-500" : "text-amber-500"}`} />
        <h3 className="mb-1 text-lg font-semibold">{title}</h3>
        <p className="mb-5 text-sm text-slate-500">{message}</p>
        <div className="flex justify-center gap-2">
          <button className="btn-light" onClick={onClose}>Annuler</button>
          <button className={danger ? "btn-danger" : "btn-primary"} onClick={onConfirm}>Confirmer</button>
        </div>
      </div>
    </div>
  );
}

/* ---------------- Field ---------------- */
export function Field({ label, error, children, className = "" }) {
  return (
    <div className={className}>
      {label && <label className="label">{label}</label>}
      {children}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}

/* ---------------- Toast ---------------- */
const ToastCtx = createContext(null);
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const push = useCallback((type, msg) => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, type, msg }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4000);
  }, []);
  const toast = {
    success: (m) => push("success", m),
    error: (m) => push("error", m),
    info: (m) => push("info", m),
  };
  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-emerald-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    info: <Info className="h-5 w-5 text-sky-500" />,
  };
  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
        {toasts.map((t) => (
          <div key={t.id} className="flex items-center gap-2 rounded-lg bg-white px-4 py-3 text-sm shadow-soft">
            {icons[t.type]} <span className="text-slate-700">{t.msg}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}
export const useToast = () => useContext(ToastCtx);

/* ---------------- Page header ---------------- */
export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 className="text-xl font-bold text-slate-800">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

/* ---------------- Empty ---------------- */
export function Empty({ message = "Aucune donnée." }) {
  return <div className="py-12 text-center text-sm text-slate-400">{message}</div>;
}

/* ---------------- Pagination ---------------- */
export function Pagination({ count, pageSize = 12, page, onChange }) {
  const pages = Math.ceil(count / pageSize);
  if (pages <= 1) return null;
  return (
    <div className="mt-4 flex items-center justify-center gap-2 text-sm">
      <button className="btn-light btn-sm" disabled={page <= 1} onClick={() => onChange(page - 1)}>«</button>
      <span className="text-slate-500">Page {page} / {pages}</span>
      <button className="btn-light btn-sm" disabled={page >= pages} onClick={() => onChange(page + 1)}>»</button>
    </div>
  );
}
