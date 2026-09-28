export default function TopBar() {
    return (
        <header
            style={{
                position: "absolute",
                top: 20,
                left: 30,
                right: 30,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                zIndex: 100
            }}
        >
            <h2 style={{ color: "var(--primary)" }}>
                BOB
            </h2>

            <div>
                SYSTEM ONLINE
            </div>
        </header>
    );
}