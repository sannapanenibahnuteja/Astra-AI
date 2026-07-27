import "./MessageList.css";

import useChatStore from "../../store/chatStore";

import MessageBubble from "./MessageBubble";

export default function MessageList() {

  const messages = useChatStore((state) => state.messages);

  return (
    <div className="message-list">

      {messages.map((msg) => (
        <MessageBubble
          key={msg.id}
          message={msg}
        />
      ))}

    </div>
  );
}