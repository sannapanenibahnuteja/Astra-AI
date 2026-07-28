import SettingsSection from "./SettingsSection";
import useVoiceStore from "../../store/voiceStore";

export default function VoiceSettings() {
  const mode = useVoiceStore((s) => s.mode);
  const setMode = useVoiceStore((s) => s.setMode);

  return (
    <SettingsSection title="🎤 Voice">
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "18px",
        }}
      >
        <label>
          <input
            type="radio"
            checked={mode === "silent"}
            onChange={() => setMode("silent")}
          />

          {" "}Silent
        </label>

        <label>
          <input
            type="radio"
            checked={mode === "manual"}
            onChange={() => setMode("manual")}
          />

          {" "}Manual
        </label>

        <label>
          <input
            type="radio"
            checked={mode === "auto"}
            onChange={() => setMode("auto")}
          />

          {" "}Auto Speak
        </label>
      </div>
    </SettingsSection>
  );
}