import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useBooks } from "../hooks/useBooks";
import BookFormModal from "../components/BookFormModal";

const STATUSES = [
  { value: "", label: "All Books" },
  { value: "want_to_read", label: "Want to Read", color: "#6B7280" },
  { value: "reading", label: "Reading", color: "#2563EB" },
  { value: "finished", label: "Finished", color: "#059669" },
  { value: "abandoned", label: "Abandoned", color: "#DC2626" },
];

const STATUS_MAP = Object.fromEntries(STATUSES.filter(s => s.value).map(s => [s.value, s]));

function Stars({ rating }) {
  if (!rating) return <span style={{ color: "#D1D5DB" }}>—</span>;
  return (
    <span style={{ color: "#F59E0B", letterSpacing: 1 }}>
      {"★".repeat(rating)}<span style={{ color: "#E5E7EB" }}>{"★".repeat(5 - rating)}</span>
    </span>
  );
}

function StatCard({ label, value, accent }) {
  return (
    <div style={{ ...s.statCard, borderTop: `3px solid ${accent || "#E5E7EB"}` }}>
      <div style={s.statLabel}>{label}</div>
      <div style={s.statValue}>{value}</div>
    </div>
  );
}

function BookRow({ book, onEdit, onDelete }) {
  const [deleting, setDeleting] = useState(false);
  const status = STATUS_MAP[book.status];

  const handleDelete = async () => {
    if (!window.confirm(`Remove "${book.title}"?`)) return;
    setDeleting(true);
    await onDelete(book.id);
  };

  return (
    <tr style={s.tr}>
      <td style={s.td}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {book.cover_url ? (
            <img src={book.cover_url} alt="" style={s.cover} onError={(e) => { e.target.style.display = "none"; }} />
          ) : (
            <div style={s.coverPlaceholder}>📖</div>
          )}
          <div>
            <div style={s.bookTitle}>{book.title}</div>
            {book.isbn && <div style={s.isbnText}>ISBN: {book.isbn}</div>}
          </div>
        </div>
      </td>
      <td style={s.td}><span style={s.author}>{book.author}</span></td>
      <td style={s.td}>
        <span style={{ ...s.badge, color: status?.color, borderColor: status?.color }}>
          {status?.label || book.status}
        </span>
      </td>
      <td style={s.td}><Stars rating={book.rating} /></td>
      <td style={{ ...s.td, color: "#9CA3AF", fontSize: 13 }}>
        {book.page_count ? book.page_count.toLocaleString() : "—"}
      </td>
      <td style={{ ...s.td, color: "#9CA3AF", fontSize: 13 }}>
        {book.date_finished || book.date_added || "—"}
      </td>
      <td style={s.td}>
        <div style={{ display: "flex", gap: 8 }}>
          <button style={s.editBtn} onClick={() => onEdit(book)}>Edit</button>
          <button style={s.deleteBtn} onClick={handleDelete} disabled={deleting}>
            {deleting ? "…" : "Delete"}
          </button>
        </div>
      </td>
    </tr>
  );
}

export default function LibraryPage() {
  const { user, logout } = useAuth();
  const [statusFilter, setStatusFilter] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingBook, setEditingBook] = useState(null);
  const { books, stats, loading, error, addBook, updateBook, deleteBook } = useBooks(
    statusFilter ? { status: statusFilter } : {}
  );

  const openAdd = () => { setEditingBook(null); setShowModal(true); };
  const openEdit = (book) => { setEditingBook(book); setShowModal(true); };
  const closeModal = () => { setShowModal(false); setEditingBook(null); };

  const handleSave = (data) =>
    editingBook ? updateBook(editingBook.id, data) : addBook(data);

  return (
    <div style={s.page}>
      {/* Header */}
      <header style={s.header}>
        <div style={s.headerLeft}>
          <span style={s.logo}>📚</span>
          <span style={s.appName}>BookLog</span>
        </div>
        <div style={s.headerRight}>
          <span style={s.userInfo}>{user?.name || user?.email}</span>
          <button style={s.logoutBtn} onClick={logout}>Sign Out</button>
        </div>
      </header>

      <main style={s.main}>
        {/* Stats */}
        {stats && (
          <div style={s.statsGrid}>
            <StatCard label="Total Books" value={stats.total ?? 0} accent="#6B7280" />
            <StatCard label="Finished" value={stats.finished ?? 0} accent="#059669" />
            <StatCard label="Reading" value={stats.reading ?? 0} accent="#2563EB" />
            <StatCard label="Avg Rating" value={stats.avg_rating ? `${stats.avg_rating} ★` : "—"} accent="#F59E0B" />
            <StatCard label="Pages Read" value={(stats.total_pages ?? 0).toLocaleString()} accent="#7C3AED" />
          </div>
        )}

        {/* Toolbar */}
        <div style={s.toolbar}>
          <div style={s.filterGroup}>
            {STATUSES.map((st) => (
              <button
                key={st.value}
                style={s.filterBtn(statusFilter === st.value)}
                onClick={() => setStatusFilter(st.value)}
              >
                {st.label}
              </button>
            ))}
          </div>
          <button style={s.addBtn} onClick={openAdd}>+ Add Book</button>
        </div>

        {/* Error */}
        {error && <div style={s.errorBox}>{error}</div>}

        {/* Table */}
        {loading ? (
          <div style={s.empty}>Loading your library…</div>
        ) : books.length === 0 ? (
          <div style={s.empty}>
            {statusFilter ? "No books with this status." : "Your library is empty. Add your first book!"}
          </div>
        ) : (
          <div style={s.tableWrap}>
            <table style={s.table}>
              <thead>
                <tr>
                  {["Book", "Author", "Status", "Rating", "Pages", "Date", ""].map((h) => (
                    <th key={h} style={s.th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {books.map((book) => (
                  <BookRow key={book.id} book={book} onEdit={openEdit} onDelete={deleteBook} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {showModal && (
        <BookFormModal book={editingBook} onSave={handleSave} onClose={closeModal} />
      )}
    </div>
  );
}

const s = {
  page: {
    minHeight: "100vh",
    backgroundColor: "#F9FAFB",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    color: "#111827",
  },
  header: {
    backgroundColor: "#fff",
    borderBottom: "1px solid #E5E7EB",
    padding: "0 32px",
    height: 56,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    position: "sticky",
    top: 0,
    zIndex: 10,
  },
  headerLeft: { display: "flex", alignItems: "center", gap: 10 },
  logo: { fontSize: 22 },
  appName: { fontSize: 18, fontWeight: 700, color: "#111827" },
  headerRight: { display: "flex", alignItems: "center", gap: 14 },
  userInfo: { fontSize: 14, color: "#6B7280" },
  logoutBtn: {
    padding: "5px 14px", border: "1px solid #E5E7EB", borderRadius: 6,
    backgroundColor: "transparent", fontSize: 13, color: "#374151",
    cursor: "pointer",
  },
  main: { maxWidth: 1100, margin: "0 auto", padding: "28px 32px" },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: "#fff", border: "1px solid #E5E7EB",
    borderRadius: 10, padding: "14px 18px",
  },
  statLabel: { fontSize: 11, fontWeight: 600, color: "#9CA3AF", textTransform: "uppercase", letterSpacing: "0.5px" },
  statValue: { fontSize: 26, fontWeight: 700, color: "#111827", marginTop: 4 },
  toolbar: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    marginBottom: 16, flexWrap: "wrap", gap: 10,
  },
  filterGroup: { display: "flex", gap: 6, flexWrap: "wrap" },
  filterBtn: (active) => ({
    padding: "6px 14px", border: `1px solid ${active ? "#2563EB" : "#E5E7EB"}`,
    borderRadius: 6, backgroundColor: active ? "#EFF6FF" : "#fff",
    color: active ? "#2563EB" : "#374151", fontSize: 13,
    cursor: "pointer", fontWeight: active ? 600 : 400, transition: "all 0.15s",
  }),
  addBtn: {
    padding: "8px 18px", backgroundColor: "#2563EB", color: "#fff",
    border: "none", borderRadius: 7, fontSize: 14, fontWeight: 600,
    cursor: "pointer",
  },
  errorBox: {
    backgroundColor: "#FEF2F2", border: "1px solid #FECACA", borderRadius: 8,
    padding: "10px 14px", fontSize: 13, color: "#DC2626", marginBottom: 16,
  },
  tableWrap: {
    backgroundColor: "#fff", border: "1px solid #E5E7EB",
    borderRadius: 10, overflow: "hidden",
  },
  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    padding: "11px 16px", textAlign: "left", fontSize: 11, fontWeight: 600,
    color: "#9CA3AF", textTransform: "uppercase", letterSpacing: "0.5px",
    borderBottom: "1px solid #F3F4F6", backgroundColor: "#FAFAFA",
  },
  tr: { borderBottom: "1px solid #F9FAFB", transition: "background 0.1s" },
  td: { padding: "13px 16px", verticalAlign: "middle" },
  cover: { width: 36, height: 48, objectFit: "cover", borderRadius: 3, flexShrink: 0 },
  coverPlaceholder: {
    width: 36, height: 48, backgroundColor: "#F3F4F6", borderRadius: 3,
    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0,
  },
  bookTitle: { fontSize: 14, fontWeight: 600, color: "#111827", lineHeight: 1.3 },
  isbnText: { fontSize: 11, color: "#9CA3AF", marginTop: 2 },
  author: { fontSize: 14, color: "#4B5563" },
  badge: {
    display: "inline-block", padding: "2px 10px", borderRadius: 12,
    fontSize: 12, border: "1px solid", fontWeight: 500,
  },
  editBtn: {
    padding: "4px 12px", border: "1px solid #E5E7EB", borderRadius: 6,
    backgroundColor: "transparent", fontSize: 12, color: "#374151", cursor: "pointer",
  },
  deleteBtn: {
    padding: "4px 12px", border: "1px solid #FECACA", borderRadius: 6,
    backgroundColor: "transparent", fontSize: 12, color: "#DC2626", cursor: "pointer",
  },
  empty: { textAlign: "center", padding: "60px 20px", color: "#9CA3AF", fontSize: 15 },
};
