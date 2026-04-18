"use client";

import { useState, useEffect } from "react";
import { Wallet, ArrowRightLeft, ShoppingCart, History, CreditCard } from "lucide-react";
import Link from "next/link";
import WalletConnect from "../components/WalletConnect";

export default function WalletPage() {
  const [principal, setPrincipal] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<any[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("arli_principal");
    if (saved) setPrincipal(saved);

    // Mock transactions
    setTransactions([
      { id: "tx-1", type: "purchase", item: "Alpha Trader Agent", amount: 2500, date: "2026-04-10", status: "confirmed" },
      { id: "tx-2", type: "sale", item: "Code Weaver NFT", amount: 800, date: "2026-04-12", status: "confirmed" },
      { id: "tx-3", type: "fee", item: "Platform Fee", amount: -50, date: "2026-04-12", status: "confirmed" },
    ]);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-indigo-900 to-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <h1 className="text-4xl font-bold">Wallet</h1>
          <p className="text-indigo-200 mt-2">Manage your ICP wallet and transactions</p>
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
              <div className="mt-4 pt-4 border-t">
                <p className="text-sm text-gray-500">Principal ID</p>
                <p className="font-mono text-sm break-all">{principal}</p>
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
                  <p className="font-medium text-sm">Transfer NFT</p>
                  <p className="text-xs text-gray-500">Send to another principal</p>
                </div>
              </Link>
            </div>
          </div>

          {/* Transaction History */}
          <div className="lg:col-span-3 bg-white rounded-xl shadow border p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-indigo-600" />
              Transaction History
            </h2>
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
          <Link href="/live-tasks" className="text-gray-600 hover:text-gray-900 text-sm">Live Tasks</Link>
          <Link href="/wallet" className="text-indigo-600 font-medium text-sm">Wallet</Link>
        </div>
      </div>
    </header>
  );
}
