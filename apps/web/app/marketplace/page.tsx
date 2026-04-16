"use client";

import { useState, useEffect } from "react";
import { Upload, Search, Filter, ShoppingCart, Star, TrendingUp, Package } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Agent {
  id: string;
  agent_id: string;
  name: string;
  description?: string;
  level: number;
  tier: string;
  total_xp: number;
  market_value: number;
  capabilities: string[];
  is_listed: boolean;
  listing_price?: number;
  status: string;
  created_at: string;
}

export default function Marketplace() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTier, setFilterTier] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchAgents();
    fetchStats();
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_URL}/agents?is_listed=true`);
      const data = await res.json();
      setAgents(data.items || []);
    } catch (e) {
      console.error("Failed to fetch agents");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/stats`);
      const data = await res.json();
      setStats(data);
    } catch (e) {
      console.error("Failed to fetch stats");
    }
  };

  const getTierColor = (tier: string) => {
    const colors: Record<string, string> = {
      NOVICE: "bg-gray-500",
      APPRENTICE: "bg-green-500",
      JOURNEYMAN: "bg-blue-500",
      EXPERT: "bg-purple-500",
      MASTER: "bg-orange-500",
      GRANDMASTER: "bg-red-500",
      LEGENDARY: "bg-yellow-500",
    };
    return colors[tier] || "bg-gray-500";
  };

  const filteredAgents = agents.filter((agent) => {
    if (filterTier !== "ALL" && agent.tier !== filterTier) return false;
    if (searchQuery && !agent.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />
      
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Agent Marketplace</h1>
              <p className="text-gray-600 mt-1">Buy and sell trained AI agents</p>
            </div>
            <Link
              href="/marketplace/upload"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
            >
              <Upload className="w-5 h-5" />
              List Your Agent
            </Link>
          </div>
        </div>
      </div>

      {stats && (
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard icon={<Package className="w-4 h-4" />} label="Total Agents" value={stats.total_agents} />
            <StatCard icon={<TrendingUp className="w-4 h-4" />} label="Market Value" value={`$${Math.round(stats.total_market_value || 0).toLocaleString()}`} />
            <StatCard icon={<Star className="w-4 h-4" />} label="Tasks Done" value={stats.total_tasks} />
            <StatCard icon={<ShoppingCart className="w-4 h-4" />} label="Total Sales" value={stats.total_sales} />
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="bg-white p-4 rounded-lg shadow border flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2 flex-1 min-w-[300px]">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search agents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={filterTier}
              onChange={(e) => setFilterTier(e.target.value)}
              className="border rounded px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Tiers</option>
              <option value="NOVICE">Novice</option>
              <option value="APPRENTICE">Apprentice</option>
              <option value="JOURNEYMAN">Journeyman</option>
              <option value="EXPERT">Expert</option>
              <option value="MASTER">Master</option>
              <option value="GRANDMASTER">Grandmaster</option>
              <option value="LEGENDARY">Legendary</option>
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 pb-20">
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : filteredAgents.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Package className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-xl">No agents found</p>
            <p className="mt-2">Be the first to list your agent!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map((agent) => (
              <div
                key={agent.agent_id}
                className="bg-white rounded-lg shadow border hover:shadow-lg transition overflow-hidden"
              >
                <div className="p-4 border-b">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg truncate">{agent.name}</h3>
                    <span className={`${getTierColor(agent.tier)} text-white text-xs px-2 py-1 rounded`}>
                      {agent.tier}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">{agent.description || "No description"}</p>
                </div>

                <div className="p-4 bg-gray-50">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-blue-600">{agent.level}</p>
                      <p className="text-xs text-gray-600">Level</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-600">{agent.total_xp}</p>
                      <p className="text-xs text-gray-600">XP</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-purple-600">{(agent.capabilities || []).length}</p>
                      <p className="text-xs text-gray-600">Skills</p>
                    </div>
                  </div>
                </div>

                <div className="p-4">
                  <p className="text-xs text-gray-500 mb-2">Capabilities:</p>
                  <div className="flex flex-wrap gap-1">
                    {(agent.capabilities || []).slice(0, 3).map((cap, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {cap}
                      </span>
                    ))}
                    {(agent.capabilities || []).length > 3 && (
                      <span className="text-xs text-gray-500 px-2 py-1">+{(agent.capabilities || []).length - 3}</span>
                    )}
                  </div>
                </div>

                <div className="p-4 border-t flex justify-between items-center">
                  <div>
                    <p className="text-2xl font-bold">${agent.listing_price || agent.market_value}</p>
                    <p className="text-xs text-gray-500">ID: {agent.agent_id}</p>
                  </div>
                  <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition flex items-center gap-2">
                    <ShoppingCart className="w-4 h-4" />
                    Buy
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
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
          <Link href="/skills" className="text-gray-600 hover:text-gray-900 text-sm">Skills</Link>
        </div>
      </div>
    </header>
  );
}
