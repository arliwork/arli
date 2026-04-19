"use client";

import { useState, useEffect } from "react";
import { Network, User, ChevronRight, Briefcase, DollarSign } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AgentNode {
  agent_id: string;
  name: string;
  role: string;
  level: number;
  tier: string;
  status: string;
  manager_id?: string;
  subordinates?: AgentNode[];
  monthly_budget: number;
  budget_spent: number;
  llm_cost_usd: number;
}

export default function OrgChart() {
  const [agents, setAgents] = useState<AgentNode[]>([]);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_URL}/agents`, { credentials: "include" });
      const data = await res.json();
      // Build tree structure
      const all = data.items || [];
      const byId = new Map<string, AgentNode>(all.map((a: AgentNode) => [a.agent_id, { ...a, subordinates: [] }]));
      const roots: AgentNode[] = [];
      byId.forEach((agent) => {
        if (agent.manager_id && byId.has(agent.manager_id)) {
          byId.get(agent.manager_id)!.subordinates!.push(agent);
        } else {
          roots.push(agent);
        }
      });
      setAgents(roots);
    } catch (e) {}
  };

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const renderNode = (node: AgentNode, depth: number = 0) => {
    const isExpanded = expanded.has(node.agent_id);
    const hasChildren = node.subordinates && node.subordinates.length > 0;
    const budgetPercent = node.monthly_budget > 0 ? (node.budget_spent / node.monthly_budget) * 100 : 0;

    return (
      <div key={node.agent_id} className={depth > 0 ? "ml-8 border-l-2 border-gray-200 pl-4" : ""}>
        <div className="flex items-center gap-3 p-3 bg-white rounded-lg border hover:shadow transition mb-2">
          {hasChildren && (
            <button onClick={() => toggleExpand(node.agent_id)} className="text-gray-400 hover:text-gray-600">
              <ChevronRight className={`w-4 h-4 transition ${isExpanded ? "rotate-90" : ""}`} />
            </button>
          )}
          {!hasChildren && <div className="w-4" />}

          <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm ${node.status === "paused" ? "bg-red-500" : "bg-blue-600"}`}>
            {node.name.charAt(0)}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm">{node.name}</span>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{node.role}</span>
              <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded">{node.tier}</span>
            </div>
            <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <Briefcase className="w-3 h-3" />
                Lvl {node.level}
              </span>
              <span className="flex items-center gap-1">
                <DollarSign className="w-3 h-3" />
                ${Number(node.llm_cost_usd || 0).toFixed(2)} spent
              </span>
              {node.monthly_budget > 0 && (
                <span className="flex items-center gap-1">
                  <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${budgetPercent > 90 ? "bg-red-500" : "bg-green-500"}`}
                      style={{ width: `${Math.min(budgetPercent, 100)}%` }}
                    />
                  </div>
                  <span className={budgetPercent > 90 ? "text-red-600 font-medium" : ""}>
                    {budgetPercent.toFixed(0)}%
                  </span>
                </span>
              )}
            </div>
          </div>
        </div>

        {isExpanded && hasChildren && (
          <div className="mt-2">
            {node.subordinates!.map((sub) => renderNode(sub, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <h1 className="text-4xl font-bold">Org Chart</h1>
          <p className="text-blue-200 mt-2">Company hierarchy, reporting lines, and budgets</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {agents.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Network className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No agents with reporting structure yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {agents.map((root) => renderNode(root))}
          </div>
        )}
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
          <Link href="/org-chart" className="text-blue-600 font-medium text-sm">Org Chart</Link>
          <Link href="/activity" className="text-gray-600 hover:text-gray-900 text-sm">Activity</Link>
        </div>
      </div>
    </header>
  );
}
