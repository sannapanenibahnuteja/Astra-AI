import "./MessageBubble.css";

import { useEffect, useState } from "react";

import MarkdownMessage from "../markdown/MarkdownMessage";

import {
  speak,
  stopSpeaking,
} from "../../services/voice";

import useVoiceStore from "../../store/voiceStore";

export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  const mode = useVoiceStore((state) => state.mode);

  const enabled = useVoiceStore((state) => state.enabled);

  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    if (
      !isAssistant ||
      !enabled ||
      mode !== "auto" ||
      !message.content
    )
      return;

    const utterance = speak(message.content);

    if (!utterance) return;

    setSpeaking(true);

    utterance.onend = () => {
      setSpeaking(false);
    };
  }, []);

  function handleSpeak() {
    if (speaking) {
      stopSpeaking();
      setSpeaking(false);
      return;
    }

    const utterance = speak(message.content);

    if (!utterance) return;

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

        {isAssistant &&
          enabled &&
          mode === "manual" && (
            <div className="message-actions">
              <button
                className="speak-button"
                onClick={handleSpeak}
              >
                {speaking
                  ? "⏹ Stop"
                  : "🔊 Speak"}
              </button>
            </div>
          )}
      </div>
    </div>
  );
}