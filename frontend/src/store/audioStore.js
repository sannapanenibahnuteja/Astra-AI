import { create } from "zustand";

const useAudioStore = create((set) => ({
  level: 0,

  setLevel: (level) =>
    set({
      level,
    }),
}));

export default useAudioStore;