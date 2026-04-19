"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DollarSign, TrendingUp, CheckCircle, Users } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AgentPerf {
  name: string;
  tasks: number;
  revenue: number;
}

export default function AnalyticsPage() {
  const [agents, setAgents] = useState<AgentPerf[]>([]);
  const [stats, setStats] = useState({
    totalRevenue: 0,
    totalTasks: 0,
    activeAgents: 0,
    avgTaskCost: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/agents`, { credentials: "include" }),
        fetch(`${API_URL}/stats`, { credentials: "include" }),
      ]);

      const agentsData = agentsRes.ok ? await agentsRes.json() : { items: [] };
      const statsData = statsRes.ok ? await statsRes.json() : {};

      const perf: AgentPerf[] = (agentsData.items || []).map((a: any) => ({
        name: a.name,
        tasks: a.total_tasks || 0,
        revenue: a.total_revenue || 0,
      }));

      setAgents(perf);
      setStats({
        totalRevenue: Math.round(statsData.total_revenue_generated || 0),
        totalTasks: statsData.total_tasks || 0,
        activeAgents: statsData.total_agents || 0,
        avgTaskCost: statsData.avg_task_cost || 0,
      });
    } catch (e) {
      console.error("Failed to load analytics", e);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <span className="text-xl font-bold">Analytics</span>
          </Link>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 text-sm">Dashboard</Link>
            <Link href="/billing" className="text-gray-600 hover:text-gray-900 text-sm">Billing</Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-8">Analytics Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard title="Total Revenue" value={`$${stats.totalRevenue.toLocaleString()}`} icon={<DollarSign className="w-6 h-6" />} />
          <StatsCard title="Total Tasks" value={stats.totalTasks} icon={<CheckCircle className="w-6 h-6" />} />
          <StatsCard title="Active Agents" value={stats.activeAgents} icon={<Users className="w-6 h-6" />} />
          <StatsCard title="Avg Task Cost" value={`${stats.avgTaskCost} credits`} icon={<TrendingUp className="w-6 h-6" />} />
        </div>

        <div className="bg-white rounded-xl border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Performance</h3>
          {agents.length === 0 ? (
            <p className="text-gray-500">No agent data available</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-gray-500">
                    <th className="text-left py-2">Agent</th>
                    <th className="text-right py-2">Tasks</th>
                    <th className="text-right py-2">Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((agent, i) => (
                    <tr key={i} className="border-b hover:bg-gray-50">
                      <td className="py-3 font-medium">{agent.name}</td>
                      <td className="py-3 text-right">{agent.tasks}</td>
                      <td className="py-3 text-right">${agent.revenue.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StatsCard({ title, value, icon }: { title: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="p-2 bg-blue-50 rounded-lg text-blue-600">{icon}</div>
      </div>
      <p className="text-sm text-gray-600">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
