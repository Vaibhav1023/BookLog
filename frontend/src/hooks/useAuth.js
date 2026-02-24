import { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { setLoading(false); return; }
    authApi.me().then(({ data }) => {
      if (data?.user) setUser(data.user);
      else localStorage.removeItem("token");
      setLoading(false);
    });
  }, []);

  const login = async (email, password) => {
    const { data, error } = await authApi.login({ email, password });
    if (error) return { error };
    localStorage.setItem("token", data.token);
    setUser(data.user);
    return {};
  };

  const register = async (email, password, name) => {
    const { data, error } = await authApi.register({ email, password, name });
    if (error) return { error };
    localStorage.setItem("token", data.token);
    setUser(data.user);
    return {};
  };

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
