"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Agent {
  id: string;
  agent_id: string;
  name: string;
  role: string;
  status: string;
  level: number;
  total_tasks: number;
  total_revenue: number;
  market_value: number;
}

interface Workflow {
  id: string;
  workflow_id: string;
  name: string;
  status: string;
  current_step: number;
  total_steps: number;
}

export default function Dashboard() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalRevenue: 0,
    activeAgents: 0,
    completedTasks: 0,
    totalMarketValue: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, workflowsRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/agents`),
        fetch(`${API_URL}/orchestration/workflows`),
        fetch(`${API_URL}/stats`),
      ]);

      const agentsData = agentsRes.ok ? await agentsRes.json() : { items: [] };
      const workflowsData = workflowsRes.ok ? await workflowsRes.json() : [];
      const statsData = statsRes.ok ? await statsRes.json() : {};

      setAgents(agentsData.items || []);
      setWorkflows(workflowsData || []);
      setStats({
        totalRevenue: Math.round(statsData.total_revenue_generated || 0),
        activeAgents: statsData.total_agents || 0,
        completedTasks: statsData.total_tasks || 0,
        totalMarketValue: Math.round(statsData.total_market_value || 0),
      });
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      toast.error("Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Revenue" value={`$${stats.totalRevenue.toLocaleString()}`} positive />
          <StatCard title="Active Agents" value={stats.activeAgents.toString()} positive />
          <StatCard title="Tasks Completed" value={stats.completedTasks.toString()} positive />
          <StatCard title="Market Value" value={`$${stats.totalMarketValue.toLocaleString()}`} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Agents */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">Your Agents</h2>
              <Link href="/marketplace" className="text-blue-600 hover:text-blue-700 text-sm">View All</Link>
            </div>
            <div className="divide-y">
              {agents.slice(0, 5).map((agent) => (
                <div key={agent.id} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold">
                      {agent.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                      <p className="text-xs text-gray-500">{agent.role} • Lv.{agent.level} • {agent.status}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">${agent.market_value}</div>
                    <div className="text-xs text-gray-500">{agent.total_tasks} tasks</div>
                  </div>
                </div>
              ))}
              {agents.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>No agents yet</p>
                  <Link href="/marketplace" className="text-blue-600 text-sm mt-2 inline-block">Browse Marketplace</Link>
                </div>
              )}
            </div>
          </div>

          {/* Workflows */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">Active Workflows</h2>
              <Link href="/orchestration" className="text-blue-600 hover:text-blue-700 text-sm">View All</Link>
            </div>
            <div className="divide-y">
              {workflows.slice(0, 5).map((wf) => (
                <div key={wf.id} className="py-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-900">{wf.name}</h3>
                      <p className="text-xs text-gray-500">ID: {wf.workflow_id}</p>
                    </div>
                    <StatusBadge status={wf.status} />
                  </div>
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${wf.total_steps > 0 ? (wf.current_step / wf.total_steps) * 100 : 0}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Step {wf.current_step} of {wf.total_steps}</p>
                  </div>
                </div>
              ))}
              {workflows.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>No active workflows</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <QuickActionCard title="Browse Skills" description="Add new capabilities" link="/skills" />
          <QuickActionCard title="Create Agent" description="Build a new AI agent" link="/marketplace/upload" />
          <QuickActionCard title="Run Workflow" description="Start autonomous pipeline" link="/orchestration" />
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, positive }: { title: string; value: string; positive?: boolean }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-4">
      <p className="text-sm text-gray-600 mb-1">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    running: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
    pending: "bg-gray-100 text-gray-800",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || "bg-gray-100 text-gray-800"}`}>
      {status}
    </span>
  );
}

function QuickActionCard({ title, description, link }: { title: string; description: string; link: string }) {
  return (
    <Link href={link} className="bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition-shadow block">
      <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </Link>
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
