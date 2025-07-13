import React, { useEffect, useState } from "react";
import { fetchStatus } from "../lib/apiClient";

export default function SystemStatus() {
  const [status, setStatus] = useState("loading...");
  useEffect(() => { fetchStatus().then(s => setStatus(s.status)); }, []);
  return <div>Status: {status}</div>;
}
