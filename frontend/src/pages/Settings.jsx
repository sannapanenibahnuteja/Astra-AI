import VoiceSettings from "../components/settings/VoiceSettings";

export default function Settings() {
  return (
    <div
      style={{
        padding: "40px",
        color: "white",
        maxWidth: "900px",
        margin: "0 auto",
      }}
    >
      <h1
        style={{
          marginBottom: "30px",
          fontSize: "36px",
        }}
      >
        ⚙ Settings
      </h1>

      <VoiceSettings />
    </div>
  );
}