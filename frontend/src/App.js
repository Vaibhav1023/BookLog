import { useState } from "react";
import { AuthProvider, useAuth } from "./hooks/useAuth";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import LibraryPage from "./pages/LibraryPage";

function AppRoutes() {
  const { user, loading } = useAuth();
  // showAuth: user clicked "Get Started" or "Sign In" on landing
  const [showAuth, setShowAuth] = useState(false);

  if (loading) return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color: "#9CA3AF",
    }}>
      Loading…
    </div>
  );

  if (user) return <LibraryPage />;
  if (showAuth) return <AuthPage onBack={() => setShowAuth(false)} />;
  return <LandingPage onGetStarted={() => setShowAuth(true)} />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
