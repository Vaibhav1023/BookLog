import { useState, useEffect, useCallback } from "react";
import { bookApi } from "../services/api";

export function useBooks(filters = {}) {
  const [books, setBooks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const [booksRes, statsRes] = await Promise.all([bookApi.list(filters), bookApi.stats()]);
    if (booksRes.error) setError(booksRes.error);
    else setBooks(booksRes.data || []);
    if (statsRes.data) setStats(statsRes.data);
    setLoading(false);
  }, [JSON.stringify(filters)]); // eslint-disable-line

  useEffect(() => { load(); }, [load]);

  const refreshStats = async () => {
    const { data } = await bookApi.stats();
    if (data) setStats(data);
  };

  const addBook = async (data) => {
    const { data: book, error } = await bookApi.create(data);
    if (error) return { error };
    setBooks((p) => [book, ...p]);
    await refreshStats();
    return { data: book };
  };

  const updateBook = async (id, data) => {
    const { data: book, error } = await bookApi.update(id, data);
    if (error) return { error };
    setBooks((p) => p.map((b) => (b.id === id ? book : b)));
    await refreshStats();
    return { data: book };
  };

  const deleteBook = async (id) => {
    const { error } = await bookApi.delete(id);
    if (error) return { error };
    setBooks((p) => p.filter((b) => b.id !== id));
    await refreshStats();
    return {};
  };

  return { books, stats, loading, error, addBook, updateBook, deleteBook };
}
