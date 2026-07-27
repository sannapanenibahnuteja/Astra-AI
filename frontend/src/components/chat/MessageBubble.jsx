import "./MessageBubble.css";

export default function MessageBubble({ message }) {
  return (
    <div className={`bubble ${message.role}`}>
      <div className="avatar">
        {message.role === "assistant" ? "🤖" : "🧑"}
      </div>

      <div className="message">
        {message.content}
      </div>
    </div>
  );
}