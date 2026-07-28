import "./MessageBubble.css";

import MarkdownMessage from "../markdown/MarkdownMessage";

export default function MessageBubble({ message }) {
  const isAssistant = message.role === "assistant";

  return (
    <div className={`bubble ${message.role}`}>

      <div className="avatar">
        {isAssistant ? "⚡" : "👤"}
      </div>

      <div className="message">

        <MarkdownMessage
          content={message.content}
        />

      </div>

    </div>
  );
}