import React from "react";
import ReactDOM from "react-dom/client";
import { extend } from "@react-three/fiber";

import App from "./App";
import { SettingsProvider } from "./contexts/SettingsContext";

import PlasmaMaterial from "./engine/rendering/materials/PlasmaMaterial";

extend({ PlasmaMaterial });

ReactDOM.createRoot(document.getElementById("root")).render(
  <SettingsProvider>
    <App />
  </SettingsProvider>
);