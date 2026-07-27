import { createContext, useContext, useState, useEffect } from "react";
import { themes } from "../theme/theme";

const SettingsContext = createContext();

export function SettingsProvider({ children }) {

    const [theme, setTheme] = useState("jarvis");

    useEffect(() => {

        const t = themes[theme];

        document.documentElement.style.setProperty("--primary", t.primary);
        document.documentElement.style.setProperty("--bg", t.background);
        document.documentElement.style.setProperty("--surface", t.surface);

    }, [theme]);

    return (

        <SettingsContext.Provider
            value={{
                theme,
                setTheme
            }}
        >

            {children}

        </SettingsContext.Provider>

    );

}

export function useSettings() {

    return useContext(SettingsContext);

}