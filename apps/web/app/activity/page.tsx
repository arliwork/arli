"use client";

import { useState, useEffect } from "react";
import { Activity, Clock, User, Bot, Settings, BarChart3 } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface LogEntry {
  id: string;
  actor_type: string;
  actor_name: string;
  event_type: string;
  event_description: string;
  created_at: string;
  event_metadata: any;
}

export default function ActivityPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [stats, setStats] = useState({ total: 0, breakdown: {} });
  const [filter, setFilter] = useState("");

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/activity?limit=100`);
      const data = await res.json();
      setLogs(data.items || []);
    } catch (e) {}
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/activity/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {}
  };

  const getActorIcon = (type: string) => {
    switch (type) {
      case "user": return <User className="w-4 h-4 text-blue-600" />;
      case "agent": return <Bot className="w-4 h-4 text-purple-600" />;
      default: return <Settings className="w-4 h-4 text-gray-500" />;
    }
  };

  const filtered = logs.filter((l) =>
    filter ? l.event_type.includes(filter) || l.event_description.toLowerCase().includes(filter.toLowerCase()) : true
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-slate-900 to-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <h1 className="text-4xl font-bold">Activity Log</h1>
          <p className="text-gray-300 mt-2">Audit trail — everything that happened in your company</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Activity className="w-4 h-4" />
              <span className="text-sm">Total Events</span>
            </div>
            <p className="text-2xl font-bold">{stats.total}</p>
          </div>
          {Object.entries(stats.breakdown).map(([key, val]) => (
            <div key={key} className="bg-white p-4 rounded-lg shadow border">
              <p className="text-xs text-gray-500 uppercase">{key.replace(/_/g, " ")}</p>
              <p className="text-2xl font-bold">{val as number}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-xl shadow border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-slate-600" />
              Recent Events
            </h2>
            <input
              placeholder="Filter events..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border rounded-lg px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-slate-500"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {filtered.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No activity yet</p>
            ) : (
              filtered.map((log) => (
                <div key={log.id} className="flex items-start gap-3 p-3 border rounded-lg hover:bg-gray-50 transition">
                  <div className="mt-0.5">{getActorIcon(log.actor_type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded">{log.event_type}</span>
                      <span className="text-xs text-gray-400">{log.actor_name || log.actor_type}</span>
                    </div>
                    <p className="text-sm text-gray-700">{log.event_description}</p>
                    {log.metadata && Object.keys(log.metadata).length > 0 && (
                      <p className="text-xs text-gray-400 mt-1 font-mono truncate">{JSON.stringify(log.metadata)}</p>
                    )}
                  </div>
                  <span className="text-xs text-gray-400 whitespace-nowrap flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(log.created_at).toLocaleString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function NavHeader() {
  return (
    <header className="bg-white border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
          <span className="text-lg font-bold">ARLI</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 text-sm">Dashboard</Link>
          <Link href="/marketplace" className="text-gray-600 hover:text-gray-900 text-sm">Marketplace</Link>
          <Link href="/approvals" className="text-gray-600 hover:text-gray-900 text-sm">Approvals</Link>
          <Link href="/activity" className="text-slate-600 font-medium text-sm">Activity</Link>
          <Link href="/live-tasks" className="text-gray-600 hover:text-gray-900 text-sm">Live Tasks</Link>
        </div>
      </div>
    </header>
  );
}
