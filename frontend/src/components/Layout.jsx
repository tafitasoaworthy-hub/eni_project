import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";
import {
  LayoutDashboard, GraduationCap, Users, FileSignature, CalendarDays,
  Network, FolderTree, BookOpen, Layers, CalendarCheck, Inbox, FilePen,
  FileText, Bot, Search, PenTool, LineChart, UsersRound, ClipboardList,
  LogOut, Menu, UserCircle, KeyRound, CalendarRange,
} from "lucide-react";

function Item({ to, icon: Icon, label, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition ${
          isActive ? "bg-white/10 text-white border-l-2 border-gold" : "text-slate-300 hover:bg-white/5 hover:text-white"
        }`
      }
    >
      <Icon className="h-[18px] w-[18px]" /> {label}
    </NavLink>
  );
}

function Section({ title }) {
  return <div className="px-3 pt-4 pb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">{title}</div>;
}

export default function Layout() {
  const { user, logout, roles } = useAuth();
  const { anneeCourante, enums } = useRefData();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState(false);

  const initials = (user?.full_name || user?.username || "?")
    .split(" ").map((s) => s[0]).slice(0, 2).join("").toUpperCase();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 overflow-y-auto bg-ink transition-transform md:static md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-3 border-b border-white/10 px-4 py-4">
          <img src="/logo.jpg" alt="logo" className="h-10 w-10 rounded-lg bg-white object-cover" />
          <div className="leading-tight">
            <div className="font-bold text-white">Université ENI</div>
            <div className="text-[11px] text-slate-400">Gestion Universitaire</div>
          </div>
        </div>

        <nav className="px-2 pb-8">
          <div className="pt-3" />
          <Item to="/" end icon={LayoutDashboard} label="Tableau de bord" />

          {(roles.isEtudiant || roles.isEnseignant) && (
            <Item to="/mon-emploi-du-temps" icon={CalendarDays} label="Mon emploi du temps" />
          )}

          {roles.isStaff && (
            <>
              <Section title="Scolarité" />
              <Item to="/etudiants" icon={GraduationCap} label="Étudiants" />
              <Item to="/enseignants" icon={Users} label="Enseignants" />
              <Item to="/inscriptions" icon={FileSignature} label="Inscriptions" />
              <Item to="/emplois-du-temps" icon={CalendarDays} label="Emplois du temps" />

              <Section title="Organisation" />
              <Item to="/departements" icon={Network} label="Départements" />
              <Item to="/filieres" icon={FolderTree} label="Filières" />
              <Item to="/matieres" icon={BookOpen} label="Matières" />
              {roles.isAdmin && <Item to="/niveaux" icon={Layers} label="Niveaux" />}
              {roles.isAdmin && <Item to="/annees" icon={CalendarCheck} label="Années univ." />}

              <Section title="Documents" />
              <Item to="/demandes" icon={Inbox} label="Demandes" />
              <Item to="/documents" icon={FileText} label="Documents générés" />
              <Item to="/modeles" icon={FilePen} label="Modèles" />
            </>
          )}

          <Section title="Intelligence artificielle" />
          <Item to="/chatbot" icon={Bot} label="Chatbot" />
          <Item to="/recherche" icon={Search} label="Recherche IA" />
          {roles.isStaff && <Item to="/assistant" icon={PenTool} label="Assistant admin." />}
          {roles.isStaff && <Item to="/analyse" icon={LineChart} label="Analyse IA" />}

          {roles.isAdmin && (
            <>
              <Section title="Administration" />
              <Item to="/utilisateurs" icon={UsersRound} label="Utilisateurs" />
              <Item to="/journal" icon={ClipboardList} label="Journal" />
            </>
          )}
        </nav>
      </aside>

      {open && <div className="fixed inset-0 z-30 bg-black/30 md:hidden" onClick={() => setOpen(false)} />}

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2.5">
          <button className="btn-ghost btn-sm md:hidden" onClick={() => setOpen(true)}>
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-3">
            {anneeCourante && (
              <span className="chip hidden items-center gap-1 sm:inline-flex">
                <CalendarRange className="h-3.5 w-3.5" /> {anneeCourante.libelle}
              </span>
            )}
            <span className="badge bg-emerald-100 text-emerald-700 hidden sm:inline-flex">
              <Bot className="mr-1 h-3.5 w-3.5" /> IA active
            </span>
            <div className="relative">
              <button onClick={() => setMenu((m) => !m)} className="flex items-center gap-2 rounded-lg px-1.5 py-1 hover:bg-slate-100">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-xs font-semibold text-white">{initials}</span>
                <span className="hidden text-sm font-medium text-slate-700 sm:inline">{user?.full_name}</span>
              </button>
              {menu && (
                <div className="absolute right-0 z-50 mt-1 w-52 rounded-lg border border-slate-100 bg-white py-1 shadow-soft" onMouseLeave={() => setMenu(false)}>
                  <div className="px-3 py-1.5 text-xs text-slate-400">{user?.role_display}</div>
                  <button className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-slate-50" onClick={() => { setMenu(false); nav("/profil"); }}>
                    <UserCircle className="h-4 w-4" /> Mon profil
                  </button>
                  <button className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-slate-50" onClick={() => { setMenu(false); nav("/profil?pwd=1"); }}>
                    <KeyRound className="h-4 w-4" /> Mot de passe
                  </button>
                  <button className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50" onClick={logout}>
                    <LogOut className="h-4 w-4" /> Déconnexion
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
