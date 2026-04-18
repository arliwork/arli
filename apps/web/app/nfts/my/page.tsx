"use client";

import { useState, useEffect } from "react";
import { Hexagon, Send, RotateCcw, ExternalLink, Copy, CheckCircle } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";

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

export default function MyNfts() {
  const [tokens, setTokens] = useState<NftToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNft, setSelectedNft] = useState<NftToken | null>(null);
  const [transferTo, setTransferTo] = useState("");
  const [transferring, setTransferring] = useState(false);

  useEffect(() => {
    fetchMyNfts();
  }, []);

  const fetchMyNfts = async () => {
    try {
      // TODO: Replace with real API call using connected wallet principal
      // const principal = await getConnectedPrincipal();
      // const res = await fetch(`${API_URL}/nfts/owner/${principal}`);
      // const data = await res.json();

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
      ];
      setTokens(mock);
    } catch (e) {
      console.error("Failed to fetch my NFTs");
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async () => {
    if (!selectedNft || !transferTo.trim()) return;
    setTransferring(true);
    try {
      // TODO: Replace with real canister call via backend
      // await fetch(`${API_URL}/nfts/transfer`, {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ token_id: selectedNft.token_id, to: transferTo }),
      // });
      toast.success(`NFT #${selectedNft.token_id} transfer initiated to ${transferTo}`);
      setSelectedNft(null);
      setTransferTo("");
    } catch (e) {
      toast.error("Transfer failed");
    } finally {
      setTransferring(false);
    }
  };

  const copyTokenId = (id: string) => {
    navigator.clipboard.writeText(id);
    toast.success("Token ID copied");
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

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-purple-900 to-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold">My Agent NFTs</h1>
              <p className="text-blue-200 mt-2">Manage and transfer your agent NFT collection</p>
            </div>
            <Link
              href="/nfts"
              className="bg-white/10 backdrop-blur border border-white/20 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-white/20 transition"
            >
              <Hexagon className="w-5 h-5" />
              Gallery
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6 pb-20">
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : tokens.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Hexagon className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-xl">No NFTs in your wallet</p>
            <p className="mt-2">
              Visit the{" "}
              <Link href="/marketplace" className="text-blue-600 hover:underline">
                Marketplace
              </Link>{" "}
              to buy your first agent NFT
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {tokens.map((nft) => (
              <div
                key={nft.token_id}
                className="bg-white rounded-xl shadow border overflow-hidden flex flex-col md:flex-row"
              >
                <div className="md:w-48 bg-gray-100 flex-shrink-0">
                  <img
                    src={nft.image}
                    alt={nft.name}
                    className="w-full h-full object-cover min-h-[200px]"
                  />
                </div>

                <div className="p-5 flex-1">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-bold text-lg">{nft.name}</h3>
                      <p className="text-xs text-gray-400">Token #{nft.token_id}</p>
                    </div>
                    <span
                      className={`${getTierColor(nft.tier)} text-white text-xs px-2 py-1 rounded-full font-medium`}
                    >
                      {nft.tier}
                    </span>
                  </div>

                  <p className="text-sm text-gray-600 mb-3">{nft.description}</p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {nft.attributes.map((attr, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {attr.trait_type}: {attr.value}
                      </span>
                    ))}
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                    <div className="bg-gray-50 rounded p-2">
                      <p className="font-bold text-blue-600">{nft.level}</p>
                      <p className="text-xs text-gray-500">Level</p>
                    </div>
                    <div className="bg-gray-50 rounded p-2">
                      <p className="font-bold text-green-600">${nft.market_value.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">Value</p>
                    </div>
                    <div className="bg-gray-50 rounded p-2">
                      <p className="font-bold text-purple-600">{nft.minted_at}</p>
                      <p className="text-xs text-gray-500">Minted</p>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-3 border-t">
                    <button
                      onClick={() => setSelectedNft(nft)}
                      className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm font-medium flex items-center justify-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Transfer
                    </button>
                    <button
                      onClick={() => copyTokenId(nft.token_id)}
                      className="px-3 py-2 border rounded-lg hover:bg-gray-50 transition"
                      title="Copy Token ID"
                    >
                      <Copy className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      onClick={() =>
                        window.open(`https://dashboard.internetcomputer.org/canister/${nft.agent_id}`, "_blank")
                      }
                      className="px-3 py-2 border rounded-lg hover:bg-gray-50 transition"
                      title="View on ICP"
                    >
                      <ExternalLink className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Transfer Modal */}
      {selectedNft && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold">Transfer NFT</h2>
              <button onClick={() => setSelectedNft(null)} className="text-gray-400 hover:text-gray-600">
                <RotateCcw className="w-5 h-5" />
              </button>
            </div>

            <div className="flex items-center gap-3 mb-6 bg-gray-50 p-3 rounded-lg">
              <img src={selectedNft.image} alt="" className="w-12 h-12 rounded" />
              <div>
                <p className="font-bold">{selectedNft.name}</p>
                <p className="text-xs text-gray-500">Token #{selectedNft.token_id}</p>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recipient Principal ID
              </label>
              <input
                type="text"
                value={transferTo}
                onChange={(e) => setTransferTo(e.target.value)}
                placeholder="aaaaa-aa"
                className="w-full border rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Enter the ICP Principal ID of the recipient
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setSelectedNft(null)}
                className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleTransfer}
                disabled={!transferTo.trim() || transferring}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {transferring ? (
                  <>
                    <RotateCcw className="w-4 h-4 animate-spin" />
                    Transferring...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Confirm Transfer
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
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
