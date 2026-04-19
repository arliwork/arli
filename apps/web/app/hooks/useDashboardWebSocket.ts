"use client";

import { useEffect, useRef, useState, useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = API_URL.replace("http://", "ws://").replace("https://", "wss://");

interface DashboardStats {
  total_agents: number;
  active_agents: number;
  total_market_value: number;
  total_revenue: number;
  total_tasks: number;
  total_users: number;
  timestamp: string;
}

export function useDashboardWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [liveStats, setLiveStats] = useState<DashboardStats | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const socket = new WebSocket(`${WS_URL}/ws/dashboard`);
    
    socket.onopen = () => {
      setIsConnected(true);
      console.log("[WS] Dashboard connected");
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "dashboard_stats" && msg.data) {
          setLiveStats(msg.data);
        }
      } catch (e) {
        console.error("[WS] Parse error:", e);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log("[WS] Dashboard disconnected, reconnecting in 3s...");
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    socket.onerror = (err) => {
      console.error("[WS] Error:", err);
      socket.close();
    };

    ws.current = socket;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      ws.current?.close();
    };
  }, [connect]);

  return { isConnected, liveStats };
}
