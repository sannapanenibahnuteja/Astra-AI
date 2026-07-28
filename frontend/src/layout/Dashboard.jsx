import "./Dashboard.css";

import { Routes, Route } from "react-router-dom";

import AnimatedBackground from "../components/background/AnimatedBackground";

import Sidebar from "../components/navigation/Sidebar";

import TopStatusBar from "../components/widgets/TopStatusBar";
import RightPanel from "../components/widgets/RightPanel";

import Home from "../pages/Home";
import Chat from "../pages/Chat";
import Browser from "../pages/Browser";
import Files from "../pages/Files";
import Memory from "../pages/Memory";
import Automation from "../pages/Automation";
import Themes from "../pages/Themes";
import Plugins from "../pages/Plugins";
import Settings from "../pages/Settings";

function Dashboard() {
  return (
    <>
      <AnimatedBackground />

      <div className="dashboard">

        <TopStatusBar />

        <Sidebar />

        <main>

          <Routes>

            <Route path="/" element={<Home />} />

            <Route path="/chat" element={<Chat />} />

            <Route path="/browser" element={<Browser />} />

            <Route path="/files" element={<Files />} />

            <Route path="/memory" element={<Memory />} />

            <Route path="/automation" element={<Automation />} />

            <Route path="/themes" element={<Themes />} />

            <Route path="/plugins" element={<Plugins />} />

            <Route path="/settings" element={<Settings />} />

          </Routes>

        </main>

        <RightPanel />

      </div>
    </>
  );
}

export default Dashboard;