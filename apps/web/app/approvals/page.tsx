"use client";

import { useState, useEffect } from "react";
import { CheckCircle, XCircle, MessageSquare, AlertTriangle, Clock, UserPlus, Target, DollarSign, Shield } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Approval {
  id: string;
  approval_id: string;
  approval_type: string;
  title: string;
  description: string;
  status: "pending" | "approved" | "rejected" | "revision_requested";
  payload: any;
  created_at: string;
  requested_by_agent_id?: string;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [filter, setFilter] = useState<"pending" | "all">("pending");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApprovals();
  }, [filter]);

  const fetchApprovals = async () => {
    try {
      const url = filter === "pending" ? `${API_URL}/approvals/pending` : `${API_URL}/approvals`;
      const res = await fetch(url);
      const data = await res.json();
      setApprovals(data.items || []);
    } catch (e) {
      console.error("Failed to fetch approvals");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (approvalId: string) => {
    try {
      const res = await fetch(`${API_URL}/approvals/${approvalId}/approve`, { method: "POST", credentials: "include" });
      if (res.ok) {
        toast.success("Approved");
        fetchApprovals();
      }
    } catch (e) {
      toast.error("Failed to approve");
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      const res = await fetch(`${API_URL}/approvals/${approvalId}/reject`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reason: "Rejected by board" }),
      });
      if (res.ok) {
        toast.success("Rejected");
        fetchApprovals();
      }
    } catch (e) {
      toast.error("Failed to reject");
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "hire_agent": return <UserPlus className="w-5 h-5 text-blue-600" />;
      case "ceo_strategy": return <Target className="w-5 h-5 text-purple-600" />;
      case "budget_override": return <DollarSign className="w-5 h-5 text-green-600" />;
      case "board_override": return <Shield className="w-5 h-5 text-red-600" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "hire_agent": return "Hire Agent";
      case "ceo_strategy": return "CEO Strategy";
      case "budget_override": return "Budget Override";
      case "board_override": return "Board Override";
      default: return type;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending": return <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full font-medium">Pending</span>;
      case "approved": return <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">Approved</span>;
      case "rejected": return <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-medium">Rejected</span>;
      case "revision_requested": return <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">Revision</span>;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="bg-gradient-to-r from-amber-900 to-orange-900 text-white">
        <div className="max-w-7xl mx-auto px-4 py-10">
          <h1 className="text-4xl font-bold">Approvals</h1>
          <p className="text-orange-200 mt-2">Governance layer — big decisions need your sign-off</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setFilter("pending")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${filter === "pending" ? "bg-amber-600 text-white" : "bg-white border text-gray-700 hover:bg-gray-50"}`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${filter === "all" ? "bg-amber-600 text-white" : "bg-white border text-gray-700 hover:bg-gray-50"}`}
          >
            All History
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : approvals.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-xl">No {filter} approvals</p>
            <p className="mt-2">All caught up!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {approvals.map((a) => (
              <div key={a.approval_id} className="bg-white rounded-xl shadow border p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                      {getTypeIcon(a.approval_type)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold">{a.title}</h3>
                        {getStatusBadge(a.status)}
                      </div>
                      <p className="text-xs text-gray-500">{getTypeLabel(a.approval_type)} · {a.approval_id}</p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(a.created_at).toLocaleDateString()}
                  </span>
                </div>

                <p className="text-sm text-gray-700 mb-4">{a.description}</p>

                {a.payload && Object.keys(a.payload).length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-3 mb-4 text-xs font-mono text-gray-600">
                    {JSON.stringify(a.payload, null, 2)}
                  </div>
                )}

                {a.status === "pending" && (
                  <div className="flex gap-3 pt-4 border-t">
                    <button
                      onClick={() => handleApprove(a.approval_id)}
                      className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-sm font-medium"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(a.approval_id)}
                      className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition text-sm font-medium"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                    <button
                      onClick={() => toast("Revision requested")}
                      className="flex items-center gap-2 border px-4 py-2 rounded-lg hover:bg-gray-50 transition text-sm font-medium"
                    >
                      <MessageSquare className="w-4 h-4" />
                      Request Revision
                    </button>
                  </div>
                )}
              </div>
            ))}
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
          <Link href="/nfts" className="text-gray-600 hover:text-gray-900 text-sm">NFTs</Link>
          <Link href="/approvals" className="text-amber-600 font-medium text-sm">Approvals</Link>
          <Link href="/live-tasks" className="text-gray-600 hover:text-gray-900 text-sm">Live Tasks</Link>
        </div>
      </div>
    </header>
  );
}
