import "./MessageBubble.css";

import { useState } from "react";

import MarkdownMessage from "../markdown/MarkdownMessage";

import { speak, stopSpeaking } from "../../services/voice";

export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  const [speaking, setSpeaking] = useState(false);

  function handleSpeak() {
    if (speaking) {
      stopSpeaking();
      setSpeaking(false);
      return;
    }

    const utterance = speak(message.content);

    setSpeaking(true);

    utterance.onend = () => {
      setSpeaking(false);
    };
  }

  return (
    <div className={`bubble ${message.role}`}>
      <div className="avatar">
        {isAssistant ? "⚡" : "👤"}
      </div>

      <div className="message">
        <MarkdownMessage content={message.content} />

        {isAssistant && (
          <div className="message-actions">
            <button
              className="speak-button"
              onClick={handleSpeak}
            >
              {speaking ? "⏹ Stop" : "🔊 Speak"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}