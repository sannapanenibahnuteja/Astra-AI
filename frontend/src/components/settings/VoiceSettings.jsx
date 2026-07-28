import SettingsSection from "./SettingsSection";
import useVoiceStore from "../../store/voiceStore";

export default function VoiceSettings() {
  const {
    enabled,
    mode,
    rate,
    pitch,
    volume,
    setEnabled,
    setMode,
    setRate,
    setPitch,
    setVolume,
  } = useVoiceStore();

  return (
    <SettingsSection title="🎤 Voice">
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}
      >
        <label>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
          />
          {" "}Enable Voice
        </label>

        <div>
          <h3>Voice Mode</h3>

          <label>
            <input
              type="radio"
              checked={mode === "silent"}
              onChange={() => setMode("silent")}
            />
            {" "}Silent
          </label>

          <br />

          <label>
            <input
              type="radio"
              checked={mode === "manual"}
              onChange={() => setMode("manual")}
            />
            {" "}Manual
          </label>

          <br />

          <label>
            <input
              type="radio"
              checked={mode === "auto"}
              onChange={() => setMode("auto")}
            />
            {" "}Auto Speak
          </label>
        </div>

        <div>
          <p>Speed: {rate.toFixed(1)}</p>

          <input
            type="range"
            min="0.5"
            max="2"
            step="0.1"
            value={rate}
            onChange={(e) => setRate(Number(e.target.value))}
          />
        </div>

        <div>
          <p>Pitch: {pitch.toFixed(1)}</p>

          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={pitch}
            onChange={(e) => setPitch(Number(e.target.value))}
          />
        </div>

        <div>
          <p>Volume: {volume.toFixed(1)}</p>

          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => setVolume(Number(e.target.value))}
          />
        </div>
      </div>
    </SettingsSection>
  );
}