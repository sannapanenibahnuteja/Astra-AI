import { useState } from "react";
import "./CommandInput.css";

import { streamMessage } from "../../services/chat";
import useChatStore from "../../store/chatStore";
import useAIStateStore from "../../store/aiStateStore";

export default function CommandInput() {
  const [text, setText] = useState("");

  const addMessage = useChatStore((state) => state.addMessage);
  const updateMessage = useChatStore((state) => state.updateMessage);
  const setTyping = useChatStore((state) => state.setTyping);

  const setAIState = useAIStateStore((state) => state.setState);

  async function handleSend() {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: text,
    };

    addMessage(userMessage);

    const currentMessage = text;
    setText("");

    setTyping(true);
    setAIState("thinking");

    const assistantId = Date.now() + 1;

    addMessage({
      id: assistantId,
      role: "assistant",
      content: "",
    });

    try {
      let startedSpeaking = false;

      await streamMessage(currentMessage, (partial) => {
        if (!startedSpeaking) {
          startedSpeaking = true;
          setAIState("speaking");
        }

        updateMessage(assistantId, partial);
      });

      setTyping(false);

      setTimeout(() => {
        setAIState("idle");
      }, 600);

    } catch (err) {
      setTyping(false);

      setAIState("error");

      updateMessage(
        assistantId,
        "⚠️ Unable to contact Astra backend."
      );

      console.error(err);

      setTimeout(() => {
        setAIState("idle");
      }, 1500);
    }
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