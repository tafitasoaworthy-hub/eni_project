import api from "./client";

/** Fetch a generated document PDF with auth and open it in a new tab. */
export async function openDocumentPdf(id) {
  const res = await api.get(`/documents-generes/${id}/pdf/`, { responseType: "blob" });
  const url = URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
  window.open(url, "_blank");
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}
