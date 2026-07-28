export default function SettingsSection({
  title,
  children,
}) {
  return (
    <div
      style={{
        marginBottom: "30px",
        padding: "25px",
        borderRadius: "18px",
        background: "rgba(255,255,255,.04)",
        border: "1px solid rgba(0,255,255,.12)",
      }}
    >
      <h2
        style={{
          marginBottom: "20px",
        }}
      >
        {title}
      </h2>

      {children}
    </div>
  );
}