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

  updateMessage: (id, content) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id
          ? { ...msg, content }
          : msg
      ),
    })),

  setTyping: (typing) =>
    set({
      typing,
    }),
}));

export default useChatStore;