"use client";

import { useState, useEffect, useRef } from "react";
import { Play, Loader2, CheckCircle, XCircle, Activity, Zap, Queue, History } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface LiveTask {
  task_id: string;
  agent_id: string;
  category: string;
  description: string;
  status: "queued" | "running" | "completed" | "failed";
  result?: any;
  created_at: string;
}

export default function LiveTasks() {
  const [tasks, setTasks] = useState<LiveTask[]>([]);
  const [queueStatus, setQueueStatus] = useState({ queued: 0, running: 0, completed: 0 });
  const [agentId, setAgentId] = useState("agent-001");
  const [category, setCategory] = useState("coding");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchQueueStatus();
    const interval = setInterval(fetchQueueStatus, 3000);

    // WebSocket for real-time updates
    const wsUrl = API_URL.replace("http", "ws") + "/live-tasks/ws";
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateTaskFromWs(data);
    };
    wsRef.current = ws;

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  const fetchQueueStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/live-tasks/queue`);
      const data = await res.json();
      setQueueStatus(data);
    } catch (e) {}
  };

  const updateTaskFromWs = (data: any) => {
    setTasks((prev) => {
      const existing = prev.find((t) => t.task_id === data.task_id);
      if (existing) {
        return prev.map((t) =>
          t.task_id === data.task_id ? { ...t, status: data.status, result: data.data } : t
        );
      }
      return prev;
    });
  };

  const submitTask = async () => {
    if (!description.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/live-tasks/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: agentId, category, description, parameters: {} }),
      });
      const data = await res.json();
      setTasks((prev) => [data, ...prev]);
      setDescription("");
    } catch (e) {
      console.error("Submit failed", e);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "failed":
        return <XCircle className="w-4 h-4 text-red-500" />;
      case "running":
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <Queue className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-emerald-900 to-teal-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <h1 className="text-4xl font-bold">Live Tasks</h1>
          <p className="text-emerald-200 mt-2">Real-time agent task execution with retry logic</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <StatCard icon={<Queue className="w-4 h-4" />} label="Queued" value={queueStatus.queued} />
          <StatCard icon={<Activity className="w-4 h-4" />} label="Running" value={queueStatus.running} />
          <StatCard icon={<CheckCircle className="w-4 h-4" />} label="Completed" value={queueStatus.completed} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Submit Form */}
          <div className="bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-600" />
              Submit Task
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Agent ID</label>
                <input
                  value={agentId}
                  onChange={(e) => setAgentId(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="coding">Coding</option>
                  <option value="research">Research</option>
                  <option value="content">Content</option>
                  <option value="trading">Trading</option>
                  <option value="analysis">Analysis</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  placeholder="Describe what the agent should do..."
                  className="w-full border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
              <button
                onClick={submitTask}
                disabled={submitting || !description.trim()}
                className="w-full bg-emerald-600 text-white py-2 rounded-lg hover:bg-emerald-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {submitting ? "Submitting..." : "Execute Task"}
              </button>
            </div>
          </div>

          {/* Task History */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-emerald-600" />
              Recent Tasks
            </h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {tasks.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No tasks yet. Submit your first task!</p>
              ) : (
                tasks.map((task) => (
                  <div key={task.task_id} className="border rounded-lg p-4 hover:bg-gray-50 transition">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(task.status)}
                        <span className="font-medium text-sm">{task.task_id}</span>
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{task.category}</span>
                      </div>
                      <span className="text-xs text-gray-400">{task.status}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{task.description}</p>
                    {task.result && (
                      <div className="bg-gray-50 rounded p-2 text-xs text-gray-600 font-mono whitespace-pre-wrap max-h-32 overflow-y-auto">
                        {typeof task.result.output === "string"
                          ? task.result.output
                          : JSON.stringify(task.result, null, 2)}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow border">
      <div className="flex items-center gap-2 text-gray-600 mb-1">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
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
          <Link href="/nfts" className="text-gray-600 hover:text-gray-900 text-sm">NFTs</Link>
          <Link href="/approvals" className="text-gray-600 hover:text-gray-900 text-sm">Approvals</Link>
          <Link href="/org-chart" className="text-gray-600 hover:text-gray-900 text-sm">Org Chart</Link>
          <Link href="/activity" className="text-gray-600 hover:text-gray-900 text-sm">Activity</Link>
          <Link href="/live-tasks" className="text-gray-600 hover:text-gray-900 text-sm">Live Tasks</Link>
          <Link href="/wallet" className="text-gray-600 hover:text-gray-900 text-sm">Wallet</Link>
        </div>
      </div>
    </header>
  );
}
