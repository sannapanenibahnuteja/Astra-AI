import { create } from "zustand";

const useBrowserStore = create((set) => ({
  query: "",
  summary: "",
  loading: false,
  error: "",

  setQuery: (query) =>
    set({
      query,
    }),

  setSummary: (summary) =>
    set({
      summary,
    }),

  setLoading: (loading) =>
    set({
      loading,
    }),

  setError: (error) =>
    set({
      error,
    }),
}));

export default useBrowserStore;