import { useState, useEffect, useRef } from "react";
import { searchApi } from "../services/api";

const STATUSES = [
  { value: "want_to_read", label: "Want to Read" },
  { value: "reading", label: "Reading" },
  { value: "finished", label: "Finished" },
  { value: "abandoned", label: "Abandoned" },
];
const RATABLE = new Set(["finished", "abandoned"]);

const EMPTY = {
  title: "", author: "", status: "want_to_read",
  isbn: "", rating: "", page_count: "", notes: "", cover_url: "", date_finished: "",
};

export default function BookFormModal({ book, onSave, onClose }) {
  const isEdit = Boolean(book);
  const [form, setForm] = useState(
    isEdit ? {
      title: book.title || "", author: book.author || "",
      status: book.status || "want_to_read", isbn: book.isbn || "",
      rating: book.rating ?? "", page_count: book.page_count ?? "",
      notes: book.notes || "", cover_url: book.cover_url || "",
      date_finished: book.date_finished || "",
    } : EMPTY
  );
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);
  const debounceRef = useRef(null);

  const set = (field) => (e) => {
    const value = e.target.value;
    setForm((prev) => {
      const next = { ...prev, [field]: value };
      if (field === "status" && !RATABLE.has(value)) next.rating = "";
      return next;
    });
  };

  // Debounced search
  useEffect(() => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      setSearching(true);
      const { data } = await searchApi.search(searchQuery);
      setSearchResults(data?.results || []);
      setShowResults(true);
      setSearching(false);
    }, 500);
    return () => clearTimeout(debounceRef.current);
  }, [searchQuery]);

  const fillFromResult = (result) => {
    setForm((prev) => ({
      ...prev,
      title: result.title || prev.title,
      author: result.author || prev.author,
      isbn: result.isbn || prev.isbn,
      page_count: result.page_count || prev.page_count,
      cover_url: result.cover_url || prev.cover_url,
    }));
    setSearchQuery("");
    setShowResults(false);
  };

  const handleSubmit = async () => {
    setError(null);
    setSaving(true);
    const canRate = RATABLE.has(form.status);
    const payload = {
      title: form.title.trim(),
      author: form.author.trim(),
      status: form.status,
      ...(form.isbn?.trim() && { isbn: form.isbn.trim() }),
      ...(form.rating !== "" && canRate && { rating: Number(form.rating) }),
      ...(form.page_count !== "" && { page_count: Number(form.page_count) }),
      ...(form.notes?.trim() && { notes: form.notes.trim() }),
      ...(form.cover_url?.trim() && { cover_url: form.cover_url.trim() }),
      ...(form.date_finished && { date_finished: form.date_finished }),
    };
    const { error: err } = await onSave(payload);
    setSaving(false);
    if (err) setError(err);
    else onClose();
  };

  const canRate = RATABLE.has(form.status);

  return (
    <div style={s.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={s.modal}>
        <div style={s.header}>
          <h2 style={s.title}>{isEdit ? "Edit Book" : "Add Book"}</h2>
          <button style={s.closeBtn} onClick={onClose}>✕</button>
        </div>

        <div style={s.body}>
          {!isEdit && (
            <div style={{ marginBottom: 20, position: "relative" }} ref={searchRef}>
              <label style={s.label}>Search Open Library</label>
              <div style={s.searchRow}>
                <input
                  style={s.input}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by title or author…"
                />
                {searching && <span style={s.spinner}>⟳</span>}
              </div>
              {showResults && searchResults.length > 0 && (
                <div style={s.results}>
                  {searchResults.map((r, i) => (
                    <button key={i} style={s.resultItem} onClick={() => fillFromResult(r)}>
                      <div style={s.resultTitle}>{r.title}</div>
                      <div style={s.resultMeta}>{r.author}{r.page_count ? ` · ${r.page_count} pages` : ""}</div>
                    </button>
                  ))}
                </div>
              )}
              {showResults && searchResults.length === 0 && !searching && (
                <div style={s.noResults}>No results — fill in manually below.</div>
              )}
              <div style={s.divider}><span>or fill in manually</span></div>
            </div>
          )}

          {error && <div style={s.error}>{error}</div>}

          <div style={s.row}>
            <div style={s.field}>
              <label style={s.label}>Title *</label>
              <input style={s.input} value={form.title} onChange={set("title")} placeholder="Book title" />
            </div>
            <div style={s.field}>
              <label style={s.label}>Author *</label>
              <input style={s.input} value={form.author} onChange={set("author")} placeholder="Author name" />
            </div>
          </div>

          <div style={s.row}>
            <div style={s.field}>
              <label style={s.label}>Status *</label>
              <select style={s.select} value={form.status} onChange={set("status")}>
                {STATUSES.map((st) => <option key={st.value} value={st.value}>{st.label}</option>)}
              </select>
            </div>
            <div style={s.field}>
              <label style={s.label}>
                Rating {!canRate && <span style={{ color: "#D1D5DB", fontWeight: 400 }}>(finish first)</span>}
              </label>
              <select style={{ ...s.select, opacity: canRate ? 1 : 0.5 }} value={form.rating} onChange={set("rating")} disabled={!canRate}>
                <option value="">No rating</option>
                {[1,2,3,4,5].map((n) => <option key={n} value={n}>{"★".repeat(n)} ({n})</option>)}
              </select>
            </div>
          </div>

          <div style={s.row}>
            <div style={s.field}>
              <label style={s.label}>ISBN</label>
              <input style={s.input} value={form.isbn} onChange={set("isbn")} placeholder="9780000000000" />
            </div>
            <div style={s.field}>
              <label style={s.label}>Pages</label>
              <input style={s.input} type="number" min="1" value={form.page_count} onChange={set("page_count")} placeholder="300" />
            </div>
          </div>

          {form.status === "finished" && (
            <div style={s.field}>
              <label style={s.label}>Date Finished</label>
              <input style={s.input} type="date" value={form.date_finished} onChange={set("date_finished")} />
            </div>
          )}

          <div style={s.field}>
            <label style={s.label}>Notes</label>
            <textarea style={s.textarea} value={form.notes} onChange={set("notes")} placeholder="Thoughts, quotes, notes…" rows={3} />
          </div>
        </div>

        <div style={s.footer}>
          <button style={s.cancelBtn} onClick={onClose}>Cancel</button>
          <button style={s.saveBtn} onClick={handleSubmit} disabled={saving}>
            {saving ? "Saving…" : isEdit ? "Save Changes" : "Add Book"}
          </button>
        </div>
      </div>
    </div>
  );
}

const s = {
  overlay: {
    position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.4)",
    display: "flex", alignItems: "center", justifyContent: "center",
    zIndex: 100, padding: 20,
  },
  modal: {
    backgroundColor: "#fff", borderRadius: 12, width: "100%", maxWidth: 580,
    maxHeight: "90vh", display: "flex", flexDirection: "column",
    boxShadow: "0 20px 60px rgba(0,0,0,0.15)",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  header: {
    padding: "20px 24px 16px", borderBottom: "1px solid #F3F4F6",
    display: "flex", alignItems: "center", justifyContent: "space-between",
  },
  title: { fontSize: 18, fontWeight: 700, color: "#111827", margin: 0 },
  closeBtn: {
    background: "none", border: "none", fontSize: 18, color: "#9CA3AF",
    cursor: "pointer", padding: 4, lineHeight: 1,
  },
  body: { padding: "20px 24px", overflowY: "auto", flex: 1 },
  footer: {
    padding: "16px 24px", borderTop: "1px solid #F3F4F6",
    display: "flex", justifyContent: "flex-end", gap: 10,
  },
  row: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 },
  field: { display: "flex", flexDirection: "column", gap: 5, marginBottom: 14 },
  label: { fontSize: 13, fontWeight: 500, color: "#374151" },
  input: {
    padding: "8px 10px", border: "1px solid #D1D5DB", borderRadius: 7,
    fontSize: 14, color: "#111827", outline: "none", fontFamily: "inherit",
    boxSizing: "border-box", width: "100%",
  },
  select: {
    padding: "8px 10px", border: "1px solid #D1D5DB", borderRadius: 7,
    fontSize: 14, color: "#111827", backgroundColor: "#fff", fontFamily: "inherit",
    width: "100%",
  },
  textarea: {
    padding: "8px 10px", border: "1px solid #D1D5DB", borderRadius: 7,
    fontSize: 14, color: "#111827", fontFamily: "inherit", resize: "vertical",
    width: "100%", boxSizing: "border-box",
  },
  error: {
    backgroundColor: "#FEF2F2", border: "1px solid #FECACA", borderRadius: 7,
    padding: "10px 12px", fontSize: 13, color: "#DC2626", marginBottom: 14,
  },
  cancelBtn: {
    padding: "9px 18px", border: "1px solid #D1D5DB", borderRadius: 7,
    backgroundColor: "transparent", color: "#374151", fontSize: 14,
    cursor: "pointer", fontFamily: "inherit",
  },
  saveBtn: {
    padding: "9px 20px", border: "none", borderRadius: 7,
    backgroundColor: "#2563EB", color: "#fff", fontSize: 14,
    fontWeight: 600, cursor: "pointer", fontFamily: "inherit",
  },
  searchRow: { position: "relative" },
  spinner: { position: "absolute", right: 10, top: 8, color: "#9CA3AF", animation: "spin 1s linear infinite" },
  results: {
    position: "absolute", zIndex: 10, top: "calc(100% + 4px)", left: 0, right: 0,
    backgroundColor: "#fff", border: "1px solid #E5E7EB", borderRadius: 8,
    boxShadow: "0 4px 16px rgba(0,0,0,0.1)", maxHeight: 240, overflowY: "auto",
  },
  resultItem: {
    width: "100%", padding: "10px 14px", border: "none", borderBottom: "1px solid #F9FAFB",
    backgroundColor: "transparent", textAlign: "left", cursor: "pointer",
    display: "block", fontFamily: "inherit",
  },
  resultTitle: { fontSize: 14, fontWeight: 500, color: "#111827" },
  resultMeta: { fontSize: 12, color: "#6B7280", marginTop: 2 },
  noResults: {
    position: "absolute", zIndex: 10, top: "calc(100% + 4px)", left: 0, right: 0,
    backgroundColor: "#fff", border: "1px solid #E5E7EB", borderRadius: 8,
    padding: "12px 14px", fontSize: 13, color: "#9CA3AF",
  },
  divider: {
    display: "flex", alignItems: "center", gap: 10, margin: "16px 0 0",
    fontSize: 12, color: "#9CA3AF",
    "::before": { content: '""', flex: 1, height: 1, backgroundColor: "#E5E7EB" },
  },
};
