"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Rocket, Users, Code, TrendingUp, Film, Loader2, ArrowRight, CheckCircle } from "lucide-react";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Template {
  key: string;
  name: string;
  description: string;
  pipeline_type: string;
  agent_count: number;
  agents: { role: string; name: string }[];
}

const ICONS: Record<string, any> = {
  sales: TrendingUp,
  dev: Code,
  trading: TrendingUp,
  content: Film,
};

export default function Templates() {
  const router = useRouter();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const res = await fetch(`${API_URL}/orchestration/templates`);
      const data = await res.json();
      setTemplates(data.templates || []);
    } catch (e) {
      toast.error("Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  const launchTemplate = async (key: string) => {
    setLaunching(key);
    try {
      const res = await fetch(`${API_URL}/orchestration/templates/${key}/launch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      if (data.success) {
        toast.success(`Launched ${data.template} company!`);
        // Redirect to workspace or dashboard
        setTimeout(() => router.push(`/dashboard`), 800);
      } else {
        toast.error(data.error || "Launch failed");
      }
    } catch (e) {
      toast.error("Network error");
    } finally {
      setLaunching(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <span className="text-lg font-bold">ARLI</span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/marketplace" className="text-gray-600 hover:text-gray-900">Marketplace</Link>
            <Link href="/workspace" className="text-gray-600 hover:text-gray-900">Workspace</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Launch Your AI Company</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Choose a pre-built team template and deploy a fully autonomous AI company in seconds. 
            Each template includes specialized agents, workflows, and tooling.
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {templates.map((tpl) => {
              const Icon = ICONS[tpl.key] || Rocket;
              return (
                <div
                  key={tpl.key}
                  className="bg-white rounded-xl shadow-sm border hover:shadow-md transition p-6 flex flex-col"
                >
                  <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{tpl.name}</h3>
                  <p className="text-gray-600 text-sm mb-4 flex-1">{tpl.description}</p>

                  <div className="mb-4">
                    <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                      Team ({tpl.agent_count} agents)
                    </div>
                    <div className="space-y-1">
                      {tpl.agents.slice(0, 4).map((a, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm text-gray-700">
                          <CheckCircle className="w-3.5 h-3.5 text-green-500" />
                          <span>{a.name}</span>
                          <span className="text-xs text-gray-400">({a.role})</span>
                        </div>
                      ))}
                      {tpl.agents.length > 4 && (
                        <div className="text-xs text-gray-500">+{tpl.agents.length - 4} more</div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => launchTemplate(tpl.key)}
                    disabled={!!launching}
                    className="w-full bg-blue-600 text-white py-2.5 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {launching === tpl.key ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Launching...
                      </>
                    ) : (
                      <>
                        <Rocket className="w-4 h-4" />
                        Launch Company
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Feature highlights */}
        <div className="mt-16 grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-14 h-14 bg-purple-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-7 h-7 text-purple-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-1">Full Team in 1 Click</h4>
            <p className="text-sm text-gray-600">CEO, Architects, Developers, and Ops — all spawned instantly.</p>
          </div>
          <div className="text-center">
            <div className="w-14 h-14 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <Code className="w-7 h-7 text-green-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-1">Real Code & Deployment</h4>
            <p className="text-sm text-gray-600">Agents write actual files, run tests, and deploy via Docker.</p>
          </div>
          <div className="text-center">
            <div className="w-14 h-14 bg-orange-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-7 h-7 text-orange-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-1">Evolving Workforce</h4>
            <p className="text-sm text-gray-600">Agents gain XP, level up, and increase in market value.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
