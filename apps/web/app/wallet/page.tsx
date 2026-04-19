"use client";

import { useState, useEffect } from "react";
import { Wallet, ArrowRightLeft, ShoppingCart, History, CreditCard, Hexagon } from "lucide-react";
import Link from "next/link";
import WalletConnect from "../components/WalletConnect";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Transaction {
  id: string;
  type: string;
  item: string;
  amount: number;
  date: string;
  status: string;
}

export default function WalletPage() {
  const [principal, setPrincipal] = useState<string | null>(null);
  const [balance, setBalance] = useState<number>(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("arli_principal");
    if (saved) {
      setPrincipal(saved);
      fetchBalance(saved);
    }
    fetchTransactions();
  }, []);

  const fetchBalance = async (principalId: string) => {
    try {
      const res = await fetch(`${API_URL}/wallet/balance?principal=${encodeURIComponent(principalId)}`, {
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        setBalance(data.balance_icp || 0);
      }
    } catch (e) {
      console.error("Failed to fetch balance", e);
    }
  };

  const fetchTransactions = async () => {
    try {
      // Try to fetch real transactions from marketplace sales
      const res = await fetch(`${API_URL}/marketplace/transactions`, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        const txs = (data.items || []).map((t: any, idx: number) => ({
          id: `tx-${idx}`,
          type: t.type || "purchase",
          item: t.agent_name || "Agent",
          amount: t.price || 0,
          date: t.created_at?.slice(0, 10) || new Date().toISOString().slice(0, 10),
          status: "confirmed",
        }));
        setTransactions(txs);
      } else {
        setTransactions([]);
      }
    } catch (e) {
      console.error("Failed to fetch transactions", e);
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-indigo-900 to-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <h1 className="text-4xl font-bold">ICP Wallet</h1>
          <p className="text-indigo-200 mt-2">Manage your Internet Computer wallet and agent NFT transactions</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Wallet Card */}
          <div className="bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Wallet className="w-5 h-5 text-indigo-600" />
              Connection
            </h2>
            <WalletConnect />
            {principal && (
              <div className="mt-4 pt-4 border-t space-y-2">
                <div>
                  <p className="text-sm text-gray-500">Principal ID</p>
                  <p className="font-mono text-sm break-all">{principal}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">ICP Balance</p>
                  <p className="text-2xl font-bold text-indigo-600">{balance.toFixed(4)} ICP</p>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-indigo-600" />
              Quick Actions
            </h2>
            <div className="space-y-3">
              <Link
                href="/marketplace"
                className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition"
              >
                <ShoppingCart className="w-5 h-5 text-green-600" />
                <div>
                  <p className="font-medium text-sm">Buy Agent</p>
                  <p className="text-xs text-gray-500">Purchase from marketplace</p>
                </div>
              </Link>
              <Link
                href="/nfts/my"
                className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition"
              >
                <ArrowRightLeft className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="font-medium text-sm">My NFTs</p>
                  <p className="text-xs text-gray-500">Manage your agent NFTs</p>
                </div>
              </Link>
              <Link
                href="/nfts"
                className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition"
              >
                <Hexagon className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="font-medium text-sm">NFT Gallery</p>
                  <p className="text-xs text-gray-500">Browse all agent NFTs</p>
                </div>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-600" />
              Stats
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Transactions</span>
                <span className="font-bold">{transactions.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Spent</span>
                <span className="font-bold">${transactions.filter(t => t.amount > 0).reduce((s, t) => s + t.amount, 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">NFTs Owned</span>
                <Link href="/nfts/my" className="font-bold text-blue-600 hover:underline">View →</Link>
              </div>
            </div>
          </div>

          {/* Transaction History */}
          <div className="lg:col-span-3 bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-600" />
              Transaction History
            </h2>
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : transactions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No transactions yet</p>
                <p className="text-sm mt-1">Your marketplace purchases and sales will appear here</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-gray-500">
                      <th className="text-left py-2">Type</th>
                      <th className="text-left py-2">Item</th>
                      <th className="text-right py-2">Amount</th>
                      <th className="text-right py-2">Date</th>
                      <th className="text-right py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((tx) => (
                      <tr key={tx.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 capitalize">{tx.type}</td>
                        <td className="py-3">{tx.item}</td>
                        <td className={`py-3 text-right font-medium ${tx.amount > 0 ? "text-green-600" : "text-red-600"}`}>
                          {tx.amount > 0 ? "+" : ""}${Math.abs(tx.amount).toLocaleString()}
                        </td>
                        <td className="py-3 text-right text-gray-500">{tx.date}</td>
                        <td className="py-3 text-right">
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">{tx.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
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
          <Link href="/nfts" className="text-gray-600 hover:text-gray-900 text-sm">NFTs</Link>
          <Link href="/approvals" className="text-gray-600 hover:text-gray-900 text-sm">Approvals</Link>
          <Link href="/org-chart" className="text-gray-600 hover:text-gray-900 text-sm">Org Chart</Link>
          <Link href="/activity" className="text-gray-600 hover:text-gray-900 text-sm">Activity</Link>
          <Link href="/live-tasks" className="text-gray-600 hover:text-gray-900 text-sm">Live Tasks</Link>
          <Link href="/wallet" className="text-blue-600 font-medium text-sm">Wallet</Link>
        </div>
      </div>
    </header>
  );
}
