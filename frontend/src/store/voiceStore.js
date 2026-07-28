import { create } from "zustand";

const useVoiceStore = create((set) => ({
  enabled: true,

  mode: "manual", // silent | manual | auto

  voice: "",

  rate: 1,

  pitch: 1,

  volume: 1,

  setEnabled: (enabled) => set({ enabled }),

  setMode: (mode) => set({ mode }),

  setVoice: (voice) => set({ voice }),

  setRate: (rate) => set({ rate }),

  setPitch: (pitch) => set({ pitch }),

  setVolume: (volume) => set({ volume }),
}));

export default useVoiceStore;