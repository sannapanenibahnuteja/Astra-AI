import { create } from "zustand";

const useWorkspaceStore = create((set) => ({
  activeFile: null,
  browserResults: [],
  notes: [],
  tasks: [],

  setActiveFile: (file) =>
    set({
      activeFile: file,
    }),

  setBrowserResults: (results) =>
    set({
      browserResults: results,
    }),

  addNote: (note) =>
    set((state) => ({
      notes: [...state.notes, note],
    })),

  addTask: (task) =>
    set((state) => ({
      tasks: [...state.tasks, task],
    })),
}));

export default useWorkspaceStore;