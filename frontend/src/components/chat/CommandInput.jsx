import { useState } from "react";
import "./CommandInput.css";

import { sendMessage } from "../../services/chat";
import useChatStore from "../../store/chatStore";
import useAIStateStore from "../../store/aiStateStore";

export default function CommandInput() {
  const [text, setText] = useState("");

  const addMessage = useChatStore((state) => state.addMessage);
  const setTyping = useChatStore((state) => state.setTyping);

  const setAIState = useAIStateStore((state) => state.setState);

  async function handleSend() {
    if (!text.trim()) return;

    addMessage({
      id: Date.now(),
      role: "user",
      content: text,
    });

    setTyping(true);

    // Astra starts thinking
    setAIState("thinking");

    const currentMessage = text;
    setText("");

    try {
      const reply = await sendMessage(currentMessage);

      // Astra is speaking
      setAIState("speaking");

      addMessage({
        id: Date.now() + 1,
        role: "assistant",
        content: reply,
      });

      // Return to idle after speaking
      setTimeout(() => {
        setAIState("idle");
      }, 800);

    } catch (err) {

      // Error state
      setAIState("error");

      addMessage({
        id: Date.now() + 2,
        role: "assistant",
        content: "⚠️ Unable to contact Astra backend.",
      });

      console.error(err);

      // Return to idle after a short delay
      setTimeout(() => {
        setAIState("idle");
      }, 1500);
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