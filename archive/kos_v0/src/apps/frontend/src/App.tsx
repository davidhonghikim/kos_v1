import React from "react";
import PromptPanel from "./components/PromptPanel";
import SystemStatus from "./components/SystemStatus";

export default function App() {
  return (
    <div>
      <h1>Kind AI OS</h1>
      <SystemStatus />
      <PromptPanel />
    </div>
  );
}
