import { useState } from "react";
import "./CommandInput.css";

import { sendMessage } from "../../services/chat";
import useChatStore from "../../store/chatStore";

export default function CommandInput() {
  const [text, setText] = useState("");

  const addMessage = useChatStore((state) => state.addMessage);
  const setTyping = useChatStore((state) => state.setTyping);

  async function handleSend() {
    if (!text.trim()) return;

    addMessage({
      id: Date.now(),
      role: "user",
      content: text,
    });

    setTyping(true);

    const currentMessage = text;
    setText("");

    try {
      const reply = await sendMessage(currentMessage);

      addMessage({
        id: Date.now() + 1,
        role: "assistant",
        content: reply,
      });
    } catch (err) {
      addMessage({
        id: Date.now() + 2,
        role: "assistant",
        content: "⚠️ Unable to contact Astra backend.",
      });
      console.error(err);
    }

    setTyping(false);
  }

  return (
    <div className="command-input">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
        placeholder="Ask Astra anything..."
      />

      <button onClick={handleSend}>
        Send
      </button>
    </div>
  );
}