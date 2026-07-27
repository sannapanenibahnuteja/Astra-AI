import "./ChatWindow.css";

import GlassPanel from "../ui/GlassPanel";

import MessageList from "./MessageList";

import TypingIndicator from "./TypingIndicator";

import useChatStore from "../../store/chatStore";

export default function ChatWindow() {

  const typing = useChatStore((state) => state.typing);

  return (

    <GlassPanel className="chat-window">

      <MessageList />

      {typing && <TypingIndicator />}

    </GlassPanel>

  );

}