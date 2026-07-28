export default function PageContainer({ title, children }) {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        padding: "40px",
        color: "white",
        overflowY: "auto",
      }}
    >
      <h1
        style={{
          color: "#35F6FF",
          fontSize: "34px",
          marginBottom: "30px",
        }}
      >
        {title}
      </h1>

      {children}
    </div>
  );
}