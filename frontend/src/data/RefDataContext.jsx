import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";

const RefDataCtx = createContext(null);

export function RefDataProvider({ children }) {
  const { user } = useAuth();
  const [enums, setEnums] = useState({});
  const [filieres, setFilieres] = useState([]);
  const [niveaux, setNiveaux] = useState([]);
  const [departements, setDepartements] = useState([]);
  const [annees, setAnnees] = useState([]);
  const [enseignants, setEnseignants] = useState([]);

  async function reload() {
    const unwrap = (r) => (r.status === "fulfilled" ? (r.value.data.results || r.value.data) : []);
    const [e, f, n, d, a, t] = await Promise.allSettled([
      api.get("/enums/"),
      api.get("/filieres/", { params: { page_size: 200 } }),
      api.get("/niveaux/"),
      api.get("/departements/", { params: { page_size: 200 } }),
      api.get("/annees/"),
      api.get("/enseignants/", { params: { page_size: 300 } }),
    ]);
    if (e.status === "fulfilled") setEnums(e.value.data);
    setFilieres(unwrap(f));
    setNiveaux(unwrap(n));
    setDepartements(unwrap(d));
    setAnnees(unwrap(a));
    setEnseignants(unwrap(t));
  }

  useEffect(() => {
    if (user) reload();
  }, [user]);

  const anneeCourante = annees.find((a) => a.courante);

  return (
    <RefDataCtx.Provider
      value={{ enums, filieres, niveaux, departements, annees, enseignants, anneeCourante, reload }}
    >
      {children}
    </RefDataCtx.Provider>
  );
}

export const useRefData = () => useContext(RefDataCtx);
