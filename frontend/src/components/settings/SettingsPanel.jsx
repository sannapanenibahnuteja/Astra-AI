import { useSettings } from "../../contexts/SettingsContext";

export default function SettingsPanel() {

    const { setTheme } = useSettings();

    return (

        <div
            style={{
                position: "absolute",
                right: 20,
                top: 70,
                display: "flex",
                gap: 10
            }}
        >

            <button onClick={() => setTheme("jarvis")}>
                JARVIS
            </button>

            <button onClick={() => setTheme("friday")}>
                FRIDAY
            </button>

            <button onClick={() => setTheme("matrix")}>
                MATRIX
            </button>

            <button onClick={() => setTheme("cyberpunk")}>
                CYBER
            </button>

        </div>

    );

}