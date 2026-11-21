import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const api = axios.create({ baseURL });

// Attach access token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Refresh on 401 once
let refreshing = null;
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      const refresh = localStorage.getItem("refresh");
      if (!refresh) {
        logout();
        return Promise.reject(error);
      }
      original._retry = true;
      try {
        refreshing =
          refreshing ||
          axios.post(`${baseURL}/auth/refresh/`, { refresh });
        const { data } = await refreshing;
        refreshing = null;
        localStorage.setItem("access", data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (e) {
        refreshing = null;
        logout();
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  }
);

export function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("user");
  if (!window.location.pathname.startsWith("/login")) {
    window.location.href = "/login";
  }
}

export default api;
