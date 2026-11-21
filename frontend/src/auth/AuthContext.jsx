import { createContext, useContext, useEffect, useState } from "react";
import api, { logout as doLogout } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("user")) || null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access");
    if (token) {
      api
        .get("/auth/me/")
        .then(({ data }) => {
          setUser(data);
          localStorage.setItem("user", JSON.stringify(data));
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  async function login(username, password) {
    const { data } = await api.post("/auth/login/", { username, password });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }

  function logout() {
    setUser(null);
    doLogout();
  }

  const roles = {
    isAdmin: user?.role === "ADMIN" || user?.is_superuser,
    isScolarite: user?.role === "SCOLARITE",
    isEnseignant: user?.role === "ENSEIGNANT",
    isEtudiant: user?.role === "ETUDIANT",
  };
  roles.isStaff = roles.isAdmin || roles.isScolarite;

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout, loading, roles }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
