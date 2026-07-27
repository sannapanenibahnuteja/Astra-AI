import "./RightPanel.css";
import GlassPanel from "../ui/GlassPanel";

export default function RightPanel() {
    return (
        <aside className="right-panel">

            <GlassPanel className="panel-card">
                <h3>Memory</h3>
                <p>No memories yet</p>
            </GlassPanel>

            <GlassPanel className="panel-card">
                <h3>Today's Tasks</h3>
                <p>No tasks</p>
            </GlassPanel>

            <GlassPanel className="panel-card">
                <h3>Calendar</h3>
                <p>Nothing scheduled</p>
            </GlassPanel>

        </aside>
    );
}