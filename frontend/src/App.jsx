import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { Loading } from "./components/ui";
import Layout from "./components/Layout";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Students from "./pages/Students";
import StudentDetail from "./pages/StudentDetail";
import Teachers from "./pages/Teachers";
import Departements from "./pages/Departements";
import Filieres from "./pages/Filieres";
import Matieres from "./pages/Matieres";
import Niveaux from "./pages/Niveaux";
import Annees from "./pages/Annees";
import Enrollments from "./pages/Enrollments";
import Schedules from "./pages/Schedules";
import MySchedule from "./pages/MySchedule";
import DocumentRequests from "./pages/DocumentRequests";
import GeneratedDocuments from "./pages/GeneratedDocuments";
import DocumentGenerate from "./pages/DocumentGenerate";
import Templates from "./pages/Templates";
import Chatbot from "./pages/Chatbot";
import SmartSearch from "./pages/SmartSearch";
import AdminAssistant from "./pages/AdminAssistant";
import Analysis from "./pages/Analysis";
import UsersPage from "./pages/Users";
import AuditLog from "./pages/AuditLog";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

function Protected({ children, roles }) {
  const { user, loading, roles: r } = useAuth();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.some((role) => r[role])) {
    return <div className="card p-10 text-center text-slate-500">Accès refusé — permissions insuffisantes.</div>;
  }
  return children;
}

export default function App() {
  const { user, loading } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route
        element={
          <Protected>
            <Layout />
          </Protected>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/profil" element={<Profile />} />
        <Route path="/mon-emploi-du-temps" element={<MySchedule />} />

        <Route path="/etudiants" element={<Protected roles={["isStaff"]}><Students /></Protected>} />
        <Route path="/etudiants/:id" element={<Protected roles={["isStaff"]}><StudentDetail /></Protected>} />
        <Route path="/enseignants" element={<Protected roles={["isStaff"]}><Teachers /></Protected>} />
        <Route path="/departements" element={<Protected roles={["isStaff"]}><Departements /></Protected>} />
        <Route path="/filieres" element={<Protected roles={["isStaff"]}><Filieres /></Protected>} />
        <Route path="/matieres" element={<Protected roles={["isStaff"]}><Matieres /></Protected>} />
        <Route path="/niveaux" element={<Protected roles={["isAdmin"]}><Niveaux /></Protected>} />
        <Route path="/annees" element={<Protected roles={["isAdmin"]}><Annees /></Protected>} />
        <Route path="/inscriptions" element={<Protected roles={["isStaff"]}><Enrollments /></Protected>} />
        <Route path="/emplois-du-temps" element={<Protected roles={["isStaff"]}><Schedules /></Protected>} />

        <Route path="/demandes" element={<Protected roles={["isStaff"]}><DocumentRequests /></Protected>} />
        <Route path="/documents" element={<Protected roles={["isStaff"]}><GeneratedDocuments /></Protected>} />
        <Route path="/documents/generer/:studentId" element={<Protected roles={["isStaff"]}><DocumentGenerate /></Protected>} />
        <Route path="/modeles" element={<Protected roles={["isStaff"]}><Templates /></Protected>} />

        <Route path="/chatbot" element={<Chatbot />} />
        <Route path="/recherche" element={<SmartSearch />} />
        <Route path="/assistant" element={<Protected roles={["isStaff"]}><AdminAssistant /></Protected>} />
        <Route path="/analyse" element={<Protected roles={["isStaff"]}><Analysis /></Protected>} />

        <Route path="/utilisateurs" element={<Protected roles={["isAdmin"]}><UsersPage /></Protected>} />
        <Route path="/journal" element={<Protected roles={["isStaff"]}><AuditLog /></Protected>} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
