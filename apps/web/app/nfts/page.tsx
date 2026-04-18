"use client";

import { useState, useEffect } from "react";
import { Link as LinkIcon, Search, Filter, Hexagon, TrendingUp, Eye } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface NftToken {
  token_id: string;
  owner: string;
  agent_id: string;
  name: string;
  description: string;
  image: string;
  level: number;
  tier: string;
  market_value: number;
  minted_at: string;
  attributes: { trait_type: string; value: string }[];
}

export default function NftGallery() {
  const [tokens, setTokens] = useState<NftToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTier, setFilterTier] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState({ total_supply: 0, total_volume: 0 });

  useEffect(() => {
    fetchNfts();
    fetchStats();
  }, []);

  const fetchNfts = async () => {
    try {
      // TODO: Replace with real API call to agent_nft canister via backend
      // const res = await fetch(`${API_URL}/nfts`);
      // const data = await res.json();
      // setTokens(data.items || []);

      // Mock data for UI development
      const mock: NftToken[] = [
        {
          token_id: "1",
          owner: "aaaaa-aa",
          agent_id: "agent-001",
          name: "Alpha Trader",
          description: "Expert trading agent with 95% success rate on crypto pairs",
          image: "https://api.dicebear.com/7.x/bottts/svg?seed=alpha",
          level: 12,
          tier: "EXPERT",
          market_value: 2500,
          minted_at: "2026-04-01",
          attributes: [
            { trait_type: "Domain", value: "Trading" },
            { trait_type: "Success Rate", value: "95%" },
            { trait_type: "Tasks Completed", value: "340" },
          ],
        },
        {
          token_id: "2",
          owner: "aaaaa-aa",
          agent_id: "agent-002",
          name: "Code Weaver",
          description: "Full-stack development agent specializing in React and Rust",
          image: "https://api.dicebear.com/7.x/bottts/svg?seed=weaver",
          level: 8,
          tier: "JOURNEYMAN",
          market_value: 800,
          minted_at: "2026-04-05",
          attributes: [
            { trait_type: "Domain", value: "Development" },
            { trait_type: "Languages", value: "React, Rust" },
            { trait_type: "Tasks Completed", value: "120" },
          ],
        },
        {
          token_id: "3",
          owner: "aaaaa-aa",
          agent_id: "agent-003",
          name: "Data Oracle",
          description: "Data science agent with advanced analytics capabilities",
          image: "https://api.dicebear.com/7.x/bottts/svg?seed=oracle",
          level: 15,
          tier: "MASTER",
          market_value: 5000,
          minted_at: "2026-04-08",
          attributes: [
            { trait_type: "Domain", value: "Data Science" },
            { trait_type: "Framework", value: "PyTorch, Pandas" },
            { trait_type: "Tasks Completed", value: "560" },
          ],
        },
      ];
      setTokens(mock);
    } catch (e) {
      console.error("Failed to fetch NFTs");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    // TODO: real stats from canister
    setStats({ total_supply: 3, total_volume: 8300 });
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

  const filtered = tokens.filter((t) => {
    if (filterTier !== "ALL" && t.tier !== filterTier) return false;
    if (searchQuery && !t.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-blue-900 to-purple-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold">Agent NFT Gallery</h1>
              <p className="text-blue-200 mt-2">Collect, trade, and own proven AI agents as NFTs</p>
            </div>
            <Link
              href="/nfts/my"
              className="bg-white/10 backdrop-blur border border-white/20 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-white/20 transition"
            >
              <Hexagon className="w-5 h-5" />
              My NFTs
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard icon={<Hexagon className="w-4 h-4" />} label="Total Supply" value={stats.total_supply} />
          <StatCard icon={<TrendingUp className="w-4 h-4" />} label="Total Volume" value={`$${stats.total_volume.toLocaleString()}`} />
          <StatCard icon={<Eye className="w-4 h-4" />} label="Floor Price" value="$800" />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="bg-white p-4 rounded-lg shadow border flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2 flex-1 min-w-[300px]">
            <Search className="w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search NFTs..."
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
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Hexagon className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-xl">No NFTs found</p>
            <p className="mt-2">Be the first to mint an agent NFT!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((nft) => (
              <div
                key={nft.token_id}
                className="bg-white rounded-xl shadow border hover:shadow-lg transition overflow-hidden group"
              >
                <div className="relative aspect-square bg-gray-100 overflow-hidden">
                  <img
                    src={nft.image}
                    alt={nft.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition duration-300"
                  />
                  <div className="absolute top-3 right-3">
                    <span className={`${getTierColor(nft.tier)} text-white text-xs px-2 py-1 rounded-full font-medium`}>
                      {nft.tier}
                    </span>
                  </div>
                </div>

                <div className="p-5">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg">{nft.name}</h3>
                    <span className="text-xs text-gray-400">#{nft.token_id}</span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2 mb-3">{nft.description}</p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {nft.attributes.map((attr, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {attr.trait_type}: {attr.value}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t">
                    <div>
                      <p className="text-xs text-gray-500">Level {nft.level}</p>
                      <p className="text-xl font-bold text-blue-600">${nft.market_value.toLocaleString()}</p>
                    </div>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm font-medium">
                      View Details
                    </button>
                  </div>
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
          <Link href="/nfts" className="text-blue-600 font-medium text-sm">NFTs</Link>
          <Link href="/workspace" className="text-gray-600 hover:text-gray-900 text-sm">Workspace</Link>
        </div>
      </div>
    </header>
  );
}
