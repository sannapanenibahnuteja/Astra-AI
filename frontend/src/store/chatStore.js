import { create } from "zustand";

const useChatStore = create((set) => ({
  messages: [
    {
      id: 1,
      role: "assistant",
      content: "Hello Bhanu 👋 I'm Astra. How can I help you today?",
    },
  ],

  typing: false,

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setTyping: (typing) =>
    set({
      typing,
    }),
}));

export default useChatStore;