import { create } from "zustand";

const useAIStateStore = create((set) => ({
  state: "idle",

  setState: (value) =>
    set({
      state: value,
    }),
}));

export default useAIStateStore;