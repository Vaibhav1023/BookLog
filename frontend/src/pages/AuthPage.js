import { useState } from "react";
import { useAuth } from "../hooks/useAuth";

export default function AuthPage({ onBack }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setForm((p) => ({ ...p, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const result =
      mode === "login"
        ? await login(form.email, form.password)
        : await register(form.email, form.password, form.name);
    setLoading(false);
    if (result.error) setError(result.error);
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        {onBack && (
          <button style={styles.backBtn} onClick={onBack}>← Back</button>
        )}
        <div style={styles.logo}>📚</div>
        <h1 style={styles.title}>BookLog</h1>
        <p style={styles.subtitle}>Your personal reading log</p>

        <div style={styles.tabs}>
          <button style={styles.tab(mode === "login")} onClick={() => { setMode("login"); setError(null); }}>
            Sign In
          </button>
          <button style={styles.tab(mode === "register")} onClick={() => { setMode("register"); setError(null); }}>
            Create Account
          </button>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          {error && <div style={styles.error}>{error}</div>}

          {mode === "register" && (
            <div style={styles.field}>
              <label style={styles.label}>Name</label>
              <input style={styles.input} value={form.name} onChange={set("name")} placeholder="Your name" />
            </div>
          )}

          <div style={styles.field}>
            <label style={styles.label}>Email</label>
            <input style={styles.input} type="email" value={form.email} onChange={set("email")} placeholder="you@example.com" required />
          </div>

          <div style={styles.field}>
            <label style={styles.label}>Password {mode === "register" && <span style={styles.hint}>(min 8 characters)</span>}</label>
            <input style={styles.input} type="password" value={form.password} onChange={set("password")} placeholder="••••••••" required />
          </div>

          <button type="submit" style={styles.submitBtn} disabled={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#F9FAFB",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: 20,
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  card: {
    backgroundColor: "#fff",
    border: "1px solid #E5E7EB",
    borderRadius: 12,
    padding: "40px 36px",
    width: "100%",
    maxWidth: 400,
    boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
  },
  backBtn: {
    background: "none", border: "none", color: "#6B7280", fontSize: 13,
    cursor: "pointer", padding: "0 0 12px", fontFamily: "inherit", textAlign: "left",
  },
  logo: { fontSize: 40, textAlign: "center", marginBottom: 8 },
  title: {
    fontSize: 24,
    fontWeight: 700,
    textAlign: "center",
    color: "#111827",
    margin: 0,
  },
  subtitle: {
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
    marginTop: 4,
    marginBottom: 28,
  },
  tabs: {
    display: "flex",
    backgroundColor: "#F3F4F6",
    borderRadius: 8,
    padding: 3,
    marginBottom: 24,
  },
  tab: (active) => ({
    flex: 1,
    padding: "7px 0",
    border: "none",
    borderRadius: 6,
    backgroundColor: active ? "#fff" : "transparent",
    color: active ? "#111827" : "#6B7280",
    fontWeight: active ? 600 : 400,
    fontSize: 14,
    cursor: "pointer",
    boxShadow: active ? "0 1px 2px rgba(0,0,0,0.08)" : "none",
    transition: "all 0.15s",
  }),
  form: { display: "flex", flexDirection: "column", gap: 16 },
  field: { display: "flex", flexDirection: "column", gap: 5 },
  label: { fontSize: 13, fontWeight: 500, color: "#374151" },
  hint: { fontWeight: 400, color: "#9CA3AF", marginLeft: 4 },
  input: {
    padding: "9px 12px",
    border: "1px solid #D1D5DB",
    borderRadius: 8,
    fontSize: 14,
    color: "#111827",
    outline: "none",
    transition: "border 0.15s",
    fontFamily: "inherit",
  },
  error: {
    backgroundColor: "#FEF2F2",
    border: "1px solid #FECACA",
    borderRadius: 8,
    padding: "10px 12px",
    fontSize: 13,
    color: "#DC2626",
  },
  submitBtn: {
    padding: "10px 0",
    backgroundColor: "#2563EB",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    marginTop: 4,
    fontFamily: "inherit",
    transition: "background 0.15s",
  },
};
