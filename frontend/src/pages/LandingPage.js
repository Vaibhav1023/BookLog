import { useState } from "react";

export default function LandingPage({ onGetStarted }) {
  const [hovered, setHovered] = useState(null);

  const features = [
    { icon: "📖", title: "Track Every Book", desc: "Log what you're reading, want to read, finished, or abandoned." },
    { icon: "⭐", title: "Rate & Review", desc: "Rate books 1–5 stars once you've finished or abandoned them." },
    { icon: "🔍", title: "Open Library Search", desc: "Search millions of books and auto-fill details instantly." },
    { icon: "📊", title: "Reading Stats", desc: "See your total books, pages read, and average rating at a glance." },
  ];

  const steps = [
    { n: "1", text: "Create your free account" },
    { n: "2", text: "Search for a book or add manually" },
    { n: "3", text: "Track your reading progress" },
  ];

  return (
    <div style={s.page}>
      {/* Nav */}
      <nav style={s.nav}>
        <div style={s.navInner}>
          <div style={s.brand}>📚 BookLog</div>
          <button style={s.navBtn} onClick={onGetStarted}>Sign In</button>
        </div>
      </nav>

      {/* Hero */}
      <section style={s.hero}>
        <div style={s.heroInner}>
          <div style={s.badge}>Personal Reading Log</div>
          <h1 style={s.heroTitle}>
            Your books,<br />
            <span style={s.accent}>beautifully tracked.</span>
          </h1>
          <p style={s.heroSub}>
            A clean, private reading log. Track what you're reading,
            rate what you've finished, and never lose track of what's next.
          </p>
          <div style={s.heroActions}>
            <button
              style={{ ...s.ctaBtn, ...(hovered === "cta" ? s.ctaBtnHover : {}) }}
              onMouseEnter={() => setHovered("cta")}
              onMouseLeave={() => setHovered(null)}
              onClick={onGetStarted}
            >
              Get Started — it's free
            </button>
            <span style={s.heroNote}>No credit card. No ads. Just your books.</span>
          </div>
        </div>

        {/* Mock UI preview */}
        <div style={s.mockWrap}>
          <div style={s.mockCard}>
            <div style={s.mockHeader}>
              <div style={s.mockDot("#EF4444")} />
              <div style={s.mockDot("#F59E0B")} />
              <div style={s.mockDot("#10B981")} />
              <span style={s.mockTitle}>My Library</span>
            </div>
            <div style={s.mockStats}>
              {[["12", "Books"], ["4", "Finished"], ["4.2★", "Avg"]].map(([v, l]) => (
                <div key={l} style={s.mockStat}>
                  <div style={s.mockStatVal}>{v}</div>
                  <div style={s.mockStatLabel}>{l}</div>
                </div>
              ))}
            </div>
            {[
              { title: "Dune", author: "Frank Herbert", status: "finished", color: "#059669", rating: "★★★★★" },
              { title: "The Name of the Wind", author: "Patrick Rothfuss", status: "reading", color: "#2563EB", rating: "" },
              { title: "Project Hail Mary", author: "Andy Weir", status: "want to read", color: "#6B7280", rating: "" },
            ].map((b) => (
              <div key={b.title} style={s.mockRow}>
                <div style={s.mockBookIcon}>📕</div>
                <div style={s.mockBookInfo}>
                  <div style={s.mockBookTitle}>{b.title}</div>
                  <div style={s.mockBookAuthor}>{b.author}</div>
                </div>
                <div style={{ ...s.mockBadge, color: b.color, borderColor: b.color }}>
                  {b.status}
                </div>
                {b.rating && <div style={s.mockRating}>{b.rating}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={s.features}>
        <div style={s.sectionInner}>
          <h2 style={s.sectionTitle}>Everything you need. Nothing you don't.</h2>
          <div style={s.featureGrid}>
            {features.map((f) => (
              <div key={f.title} style={s.featureCard}>
                <div style={s.featureIcon}>{f.icon}</div>
                <h3 style={s.featureTitle}>{f.title}</h3>
                <p style={s.featureDesc}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section style={s.how}>
        <div style={s.sectionInner}>
          <h2 style={s.sectionTitle}>Up and running in seconds.</h2>
          <div style={s.steps}>
            {steps.map((step, i) => (
              <div key={i} style={s.step}>
                <div style={s.stepNum}>{step.n}</div>
                <div style={s.stepText}>{step.text}</div>
                {i < steps.length - 1 && <div style={s.stepArrow}>→</div>}
              </div>
            ))}
          </div>
          <button style={s.ctaBtn} onClick={onGetStarted}>
            Create Your Library
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer style={s.footer}>
        <span>📚 BookLog</span>
        <span style={{ color: "#9CA3AF" }}>Your personal reading log.</span>
      </footer>
    </div>
  );
}

const s = {
  page: {
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    color: "#111827",
    backgroundColor: "#fff",
  },
  nav: {
    borderBottom: "1px solid #F3F4F6",
    padding: "0 32px",
    position: "sticky",
    top: 0,
    backgroundColor: "#fff",
    zIndex: 10,
  },
  navInner: {
    maxWidth: 1100,
    margin: "0 auto",
    height: 56,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
  },
  brand: { fontSize: 18, fontWeight: 700, color: "#111827" },
  navBtn: {
    padding: "6px 18px",
    border: "1px solid #E5E7EB",
    borderRadius: 7,
    backgroundColor: "transparent",
    fontSize: 14,
    cursor: "pointer",
    color: "#374151",
    fontFamily: "inherit",
  },
  hero: {
    maxWidth: 1100,
    margin: "0 auto",
    padding: "80px 32px 60px",
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 60,
    alignItems: "center",
  },
  heroInner: { display: "flex", flexDirection: "column", gap: 20 },
  badge: {
    display: "inline-block",
    padding: "4px 12px",
    backgroundColor: "#EFF6FF",
    color: "#2563EB",
    borderRadius: 20,
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: "0.5px",
    width: "fit-content",
  },
  heroTitle: {
    fontSize: 52,
    fontWeight: 800,
    lineHeight: 1.1,
    color: "#111827",
    margin: 0,
  },
  accent: { color: "#2563EB" },
  heroSub: {
    fontSize: 17,
    color: "#6B7280",
    lineHeight: 1.6,
    maxWidth: 440,
    margin: 0,
  },
  heroActions: { display: "flex", flexDirection: "column", gap: 10, alignItems: "flex-start" },
  ctaBtn: {
    padding: "13px 28px",
    backgroundColor: "#2563EB",
    color: "#fff",
    border: "none",
    borderRadius: 9,
    fontSize: 15,
    fontWeight: 600,
    cursor: "pointer",
    fontFamily: "inherit",
    transition: "background 0.15s",
  },
  ctaBtnHover: { backgroundColor: "#1D4ED8" },
  heroNote: { fontSize: 13, color: "#9CA3AF" },

  // Mock card
  mockWrap: { display: "flex", justifyContent: "center" },
  mockCard: {
    backgroundColor: "#fff",
    border: "1px solid #E5E7EB",
    borderRadius: 14,
    padding: 20,
    width: 340,
    boxShadow: "0 20px 60px rgba(0,0,0,0.10)",
  },
  mockHeader: {
    display: "flex",
    alignItems: "center",
    gap: 6,
    marginBottom: 16,
    paddingBottom: 12,
    borderBottom: "1px solid #F3F4F6",
  },
  mockDot: (color) => ({
    width: 10,
    height: 10,
    borderRadius: "50%",
    backgroundColor: color,
  }),
  mockTitle: { marginLeft: 8, fontSize: 13, fontWeight: 600, color: "#374151" },
  mockStats: {
    display: "flex",
    gap: 0,
    marginBottom: 16,
    backgroundColor: "#F9FAFB",
    borderRadius: 8,
    overflow: "hidden",
  },
  mockStat: {
    flex: 1,
    padding: "10px 0",
    textAlign: "center",
    borderRight: "1px solid #F3F4F6",
  },
  mockStatVal: { fontSize: 18, fontWeight: 700, color: "#111827" },
  mockStatLabel: { fontSize: 10, color: "#9CA3AF", marginTop: 2 },
  mockRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 0",
    borderBottom: "1px solid #F9FAFB",
  },
  mockBookIcon: { fontSize: 20 },
  mockBookInfo: { flex: 1, minWidth: 0 },
  mockBookTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: "#111827",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  mockBookAuthor: { fontSize: 11, color: "#9CA3AF", marginTop: 1 },
  mockBadge: {
    fontSize: 10,
    border: "1px solid",
    borderRadius: 10,
    padding: "2px 7px",
    whiteSpace: "nowrap",
    fontWeight: 500,
  },
  mockRating: { fontSize: 11, color: "#F59E0B", whiteSpace: "nowrap" },

  // Features
  features: {
    backgroundColor: "#F9FAFB",
    padding: "72px 32px",
  },
  sectionInner: {
    maxWidth: 1100,
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 40,
  },
  sectionTitle: { fontSize: 32, fontWeight: 700, color: "#111827", textAlign: "center", margin: 0 },
  featureGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 20,
    width: "100%",
  },
  featureCard: {
    backgroundColor: "#fff",
    border: "1px solid #E5E7EB",
    borderRadius: 12,
    padding: "24px 20px",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  featureIcon: { fontSize: 28 },
  featureTitle: { fontSize: 15, fontWeight: 700, color: "#111827", margin: 0 },
  featureDesc: { fontSize: 13, color: "#6B7280", lineHeight: 1.5, margin: 0 },

  // How it works
  how: {
    padding: "72px 32px",
    textAlign: "center",
  },
  steps: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    flexWrap: "wrap",
  },
  step: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  stepNum: {
    width: 36,
    height: 36,
    borderRadius: "50%",
    backgroundColor: "#2563EB",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: 700,
    fontSize: 15,
    flexShrink: 0,
  },
  stepText: { fontSize: 15, color: "#374151", fontWeight: 500 },
  stepArrow: { fontSize: 20, color: "#D1D5DB", marginLeft: 4 },

  footer: {
    borderTop: "1px solid #F3F4F6",
    padding: "20px 32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    fontSize: 14,
    color: "#374151",
    maxWidth: 1100,
    margin: "0 auto",
  },
};
