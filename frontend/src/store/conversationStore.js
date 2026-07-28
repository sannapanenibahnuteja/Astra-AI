import { create } from "zustand";

const useConversationStore = create((set) => ({
  messages: [],

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  clearMessages: () =>
    set({
      messages: [],
    }),
}));

export default useConversationStore;