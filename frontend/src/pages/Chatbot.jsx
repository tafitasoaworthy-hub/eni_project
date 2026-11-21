import { useEffect, useRef, useState } from "react";
import api from "../api/client";
import { Bot, Send, User } from "lucide-react";

const SUGGESTIONS = [
  "Quels documents pour une inscription ?",
  "Comment obtenir une attestation ?",
  "Combien d'étudiants au total ?",
];

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const boxRef = useRef(null);

  useEffect(() => { boxRef.current?.scrollTo(0, boxRef.current.scrollHeight); }, [messages, busy]);

  async function send(text) {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    const history = [...messages, { role: "user", content: q }];
    setMessages(history);
    setInput("");
    setBusy(true);
    try {
      const { data } = await api.post("/ia/chat/", { history });
      setMessages((m) => [...m, { role: "assistant", content: data.answer, via: data.via_openai }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "Erreur de communication. Réessayez." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-3xl flex-col">
      <div className="mb-3">
        <h1 className="text-xl font-bold text-slate-800">Assistant universitaire</h1>
        <p className="text-sm text-slate-500">Posez vos questions sur les inscriptions, filières, documents et emplois du temps.</p>
      </div>

      <div ref={boxRef} className="card flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="py-10 text-center text-slate-400">
            <Bot className="mx-auto mb-3 h-10 w-10" />
            <p>Bonjour ! Comment puis-je vous aider ?</p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="btn-light btn-sm" onClick={() => send(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            {m.role === "assistant" && <span className="mt-1 flex h-7 w-7 flex-none items-center justify-center rounded-full bg-brand-600 text-white"><Bot className="h-4 w-4" /></span>}
            <div className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${m.role === "user" ? "rounded-br-sm bg-brand-600 text-white" : "rounded-bl-sm bg-slate-100 text-slate-700"}`}>
              {m.content}
              {m.role === "assistant" && m.via !== undefined && (
                <div className="mt-1 text-[10px] opacity-50">{m.via ? "OpenAI" : "moteur local"}</div>
              )}
            </div>
            {m.role === "user" && <span className="mt-1 flex h-7 w-7 flex-none items-center justify-center rounded-full bg-slate-300 text-white"><User className="h-4 w-4" /></span>}
          </div>
        ))}
        {busy && <div className="flex gap-2"><span className="mt-1 flex h-7 w-7 items-center justify-center rounded-full bg-brand-600 text-white"><Bot className="h-4 w-4" /></span>
          <div className="rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-400">…</div></div>}
      </div>

      <form className="mt-3 flex gap-2" onSubmit={(e) => { e.preventDefault(); send(); }}>
        <input className="input flex-1" placeholder="Écrivez votre message..." value={input} onChange={(e) => setInput(e.target.value)} />
        <button className="btn-primary" disabled={busy}><Send className="h-4 w-4" /></button>
      </form>
    </div>
  );
}
