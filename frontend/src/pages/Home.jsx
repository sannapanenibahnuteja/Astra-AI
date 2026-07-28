import AICore from "../components/hud/AICore";
import ChatWindow from "../components/chat/ChatWindow";
import CommandInput from "../components/chat/CommandInput";

export default function Home() {
  return (
    <>
      <AICore />

      <ChatWindow />

      <CommandInput />
    </>
  );
}