import "./styles/globals.css";
import "./styles/variables.css";
import "./styles/themes.css";

import { BrowserRouter } from "react-router-dom";

import Dashboard from "./layout/Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Dashboard />
    </BrowserRouter>
  );
}