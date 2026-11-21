import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { useRefData } from "../data/RefDataContext";
import { Loading, PageHeader } from "../components/ui";
import { Link } from "react-router-dom";
import {
  BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import {
  GraduationCap, Users, Network, FolderTree, FileSignature, BookOpen,
  CalendarDays, Bot, Search,
} from "lucide-react";

const COLORS = ["#8b1a1a", "#1d6fb8", "#1f8a5b", "#c9a227", "#8a5ad2", "#b23a3a", "#3a9bd2", "#3cb37c"];

function StatCard({ icon: Icon, value, label, gradient }) {
  return (
    <div className={`relative overflow-hidden rounded-xl p-5 text-white shadow-card ${gradient}`}>
      <Icon className="absolute right-3 top-3 h-9 w-9 opacity-25" />
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-sm opacity-90">{label}</div>
    </div>
  );
}

function StudentHome({ user }) {
  return (
    <div>
      <div className="mb-6 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 p-6 text-white">
        <h2 className="text-2xl font-bold">Bienvenue, {user.full_name}</h2>
        <p className="opacity-80">Espace étudiant — Université ENI</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <Link to="/mon-emploi-du-temps" className="card flex items-center gap-3 p-5 hover:shadow-soft">
          <CalendarDays className="h-6 w-6 text-brand-600" /> Mon emploi du temps
        </Link>
        <Link to="/chatbot" className="card flex items-center gap-3 p-5 hover:shadow-soft">
          <Bot className="h-6 w-6 text-brand-600" /> Assistant virtuel
        </Link>
        <Link to="/recherche" className="card flex items-center gap-3 p-5 hover:shadow-soft">
          <Search className="h-6 w-6 text-brand-600" /> Recherche intelligente
        </Link>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user, roles } = useAuth();
  const { annees } = useRefData();
  const [stats, setStats] = useState(null);
  const [annee, setAnnee] = useState("");

  useEffect(() => {
    if (roles.isStaff) {
      api.get("/dashboard/stats/", { params: annee ? { annee } : {} }).then(({ data }) => setStats(data));
    }
  }, [annee, roles.isStaff]);

  if (!roles.isStaff) return <StudentHome user={user} />;
  if (!stats) return <Loading />;

  const c = stats.cards;
  const filiereData = stats.par_filiere.map((x) => ({ name: x.nom, nb: x.nb }));
  const niveauData = stats.par_niveau.map((x) => ({ name: x.code, value: x.nb }));
  const anneeData = stats.par_annee.map((x) => ({ name: x.libelle, nb: x.nb }));
  const docData = stats.doc_stats.map((x) => ({ name: x.statut, value: x.nb }));

  return (
    <div>
      <PageHeader
        title="Tableau de bord"
        subtitle="Vue d'ensemble de l'établissement"
        actions={
          <select className="select w-44" value={annee} onChange={(e) => setAnnee(e.target.value)}>
            <option value="">Toutes les années</option>
            {annees.map((a) => <option key={a.id} value={a.id}>{a.libelle}</option>)}
          </select>
        }
      />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <StatCard icon={GraduationCap} value={c.etudiants} label="Étudiants" gradient="bg-gradient-to-br from-brand-600 to-brand-500" />
        <StatCard icon={Users} value={c.enseignants} label="Enseignants" gradient="bg-gradient-to-br from-sky-700 to-sky-500" />
        <StatCard icon={Network} value={c.departements} label="Départements" gradient="bg-gradient-to-br from-emerald-700 to-emerald-500" />
        <StatCard icon={FolderTree} value={c.filieres} label="Filières" gradient="bg-gradient-to-br from-amber-600 to-yellow-500" />
        <StatCard icon={FileSignature} value={c.inscriptions} label="Inscriptions" gradient="bg-gradient-to-br from-violet-700 to-violet-500" />
        <StatCard icon={BookOpen} value={c.matieres} label="Matières" gradient="bg-gradient-to-br from-slate-700 to-slate-500" />
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-4">
        <MiniStat label="Inscriptions validées" value={c.inscriptions_validees} color="text-emerald-600" />
        <MiniStat label="Inscriptions en attente" value={c.inscriptions_attente} color="text-amber-600" />
        <MiniStat label="Demandes de documents" value={c.demandes} color="text-sky-600" />
        <MiniStat label="Documents générés" value={c.documents} color="text-brand-600" />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-12">
        <ChartCard title="Étudiants par filière" className="lg:col-span-7">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={filiereData} margin={{ left: -10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={60} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="nb" name="Étudiants" fill="#8b1a1a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Répartition par niveau" className="lg:col-span-5">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={niveauData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {niveauData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Legend /><Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Inscriptions par année universitaire" className="lg:col-span-7">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={anneeData} margin={{ left: -10 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="nb" name="Inscriptions" stroke="#1d6fb8" strokeWidth={2.5} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Demandes de documents par statut" className="lg:col-span-5">
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={docData} dataKey="value" nameKey="name" outerRadius={90}>
                {docData.map((_, i) => <Cell key={i} fill={["#c9a227", "#1f8a5b", "#b23a3a"][i % 3]} />)}
              </Pie>
              <Legend /><Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <Link to="/analyse" className="mt-5 flex items-center justify-between rounded-xl bg-white p-4 shadow-card hover:shadow-soft">
        <span className="flex items-center gap-2 font-medium text-slate-700"><Bot className="h-5 w-5 text-brand-600" /> Obtenir une synthèse IA des statistiques</span>
        <span className="text-brand-600">→</span>
      </Link>
    </div>
  );
}

function MiniStat({ label, value, color }) {
  return (
    <div className="card p-4">
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </div>
  );
}

function ChartCard({ title, className, children }) {
  return (
    <div className={`card p-4 ${className}`}>
      <h3 className="mb-3 text-sm font-semibold text-slate-700">{title}</h3>
      {children}
    </div>
  );
}
