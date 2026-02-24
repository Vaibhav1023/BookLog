/**
 * api.js — the only file that makes HTTP requests.
 *
 * Reads the JWT from localStorage and injects it into every
 * authenticated request. Components never handle tokens directly.
 */

const BASE = "http://localhost:5000/api";

async function request(path, options = {}, auth = true) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = localStorage.getItem("token");
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${BASE}${path}`, { ...options, headers });
    if (res.status === 204) return { data: null, error: null };

    const body = await res.json();
    if (!res.ok) {
      const message = body.errors ? body.errors.join(" • ") : body.error || `HTTP ${res.status}`;
      return { data: null, error: message };
    }
    return { data: body, error: null };
  } catch {
    return { data: null, error: "Cannot reach server. Is the backend running?" };
  }
}

export const authApi = {
  register: (data) => request("/auth/register", { method: "POST", body: JSON.stringify(data) }, false),
  login: (data) => request("/auth/login", { method: "POST", body: JSON.stringify(data) }, false),
  me: () => request("/auth/me"),
};

export const bookApi = {
  list: (params = {}) => {
    const qs = new URLSearchParams(Object.fromEntries(Object.entries(params).filter(([, v]) => v))).toString();
    return request(`/books${qs ? `?${qs}` : ""}`);
  },
  get: (id) => request(`/books/${id}`),
  stats: () => request("/books/stats"),
  create: (data) => request("/books", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/books/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id) => request(`/books/${id}`, { method: "DELETE" }),
};

export const searchApi = {
  search: (q) => request(`/search?q=${encodeURIComponent(q)}`),
};
