import "./Dashboard.css";

import AnimatedBackground from "../components/background/AnimatedBackground";

import TopStatusBar from "../components/widgets/TopStatusBar";
import RightPanel from "../components/widgets/RightPanel";

import Sidebar from "../components/navigation/Sidebar";

import AICore from "../components/hud/AICore";

import ChatWindow from "../components/chat/ChatWindow";
import CommandInput from "../components/chat/CommandInput";

import SettingsPanel from "../components/settings/SettingsPanel";

function Dashboard() {
  return (
    <>
      <AnimatedBackground />

      <div className="dashboard">

        <TopStatusBar />

        <SettingsPanel />

        <Sidebar />

        <main>

          <AICore />

          <ChatWindow />

          <CommandInput />

        </main>

        <RightPanel />

      </div>

    </>
  );
}

export default Dashboard;