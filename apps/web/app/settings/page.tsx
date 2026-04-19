"use client";

import { useState, useEffect } from "react";
import { Link, Save, Trash2, Key, Globe, Cpu, CheckCircle, AlertCircle } from "lucide-react";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PROVIDERS = [
  { id: "kimi", name: "Kimi (Moonshot AI)", icon: "🌙", description: "Kimi Coding / K2 - Best for coding tasks" },
  { id: "openai", name: "OpenAI", icon: "🤖", description: "GPT-4o, GPT-4o-mini, o3-mini" },
  { id: "anthropic", name: "Anthropic", icon: "🧠", description: "Claude 3.5 Sonnet, Claude Opus" },
  { id: "openrouter", name: "OpenRouter", icon: "🔀", description: "DeepSeek, Qwen, Gemini and more" },
  { id: "ollama", name: "Ollama (Local)", icon: "🏠", description: "Run models locally - llama3, deepseek-coder" },
];

const MODELS: Record<string, string[]> = {
  kimi: ["kimi-k2", "kimi-k1.6"],
  openai: ["gpt-4o", "gpt-4o-mini", "o3-mini"],
  anthropic: ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
  openrouter: ["deepseek/deepseek-chat", "qwen/qwen3-8b", "google/gemini-2.0-flash-001"],
  ollama: ["llama3.1", "codellama", "deepseek-coder"],
};

export default function SettingsPage() {
  const [provider, setProvider] = useState("kimi");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await fetch(`${API_URL}/auth/me/llm-config`, { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        setProvider(data.provider || "kimi");
        setModel(data.model || "");
        setBaseUrl(data.base_url || "");
      }
    } catch {
      // ignore
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      toast.error("API key is required");
      return;
    }
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/auth/me/llm-config`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider,
          api_key: apiKey,
          base_url: baseUrl || null,
          model: model || null,
        }),
      });
      if (!res.ok) throw new Error("Failed to save");
      toast.success("LLM configuration saved!");
      setApiKey(""); // Clear for security
    } catch (e) {
      toast.error("Failed to save LLM config");
    } finally {
      setSaving(false);
    }
  };

  const handleClear = async () => {
    if (!confirm("Clear your LLM config and use system defaults?")) return;
    try {
      const res = await fetch(`${API_URL}/auth/me/llm-config`, {
        method: "DELETE",
        credentials: "include",
      });
      if (res.ok) {
        toast.success("Config cleared");
        setProvider("kimi");
        setApiKey("");
        setBaseUrl("");
        setModel("");
      }
    } catch {
      toast.error("Failed to clear config");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="max-w-3xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-500 mb-8">Configure your AI providers and preferences</p>

        {/* LLM Provider Card */}
        <div className="bg-white rounded-xl shadow border p-6 mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Cpu className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold">LLM Provider</h2>
              <p className="text-sm text-gray-500">Choose your own AI provider and API key</p>
            </div>
          </div>

          {/* Provider Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
            {PROVIDERS.map((p) => (
              <button
                key={p.id}
                onClick={() => { setProvider(p.id); setModel(MODELS[p.id][0]); }}
                className={`flex items-start gap-3 p-4 border rounded-lg text-left transition ${
                  provider === p.id
                    ? "border-blue-500 bg-blue-50 ring-1 ring-blue-500"
                    : "hover:bg-gray-50"
                }`}
              >
                <span className="text-2xl">{p.icon}</span>
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-xs text-gray-500">{p.description}</p>
                </div>
              </button>
            ))}
          </div>

          {/* API Key */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Key className="w-4 h-4 inline mr-1" />
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={`Enter your ${PROVIDERS.find((p) => p.id === provider)?.name} API key`}
              className="w-full border rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Your API key is stored securely and never shared. It is only used for your own agent tasks.
            </p>
          </div>

          {/* Model Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Model (optional)</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full border rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Default model for {provider}</option>
              {MODELS[provider]?.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          {/* Base URL (optional) */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Globe className="w-4 h-4 inline mr-1" />
              Custom Base URL (optional)
            </label>
            <input
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder={`https://api.${provider}.com`}
              className="w-full border rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Only needed for self-hosted or proxy setups (e.g. Ollama at http://localhost:11434)
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Save className="w-4 h-4" />
              {saving ? "Saving..." : "Save Configuration"}
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition flex items-center gap-2 text-gray-600"
            >
              <Trash2 className="w-4 h-4" />
              Reset
            </button>
          </div>
        </div>

        {/* Info Card */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-blue-800 font-medium">How it works</p>
            <p className="text-sm text-blue-700 mt-1">
              Each user can configure their own LLM provider. When your agents run tasks, they will use
              your personal API key. Costs are tracked per-agent and deducted from your credit balance.
            </p>
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
          <Link href="/settings" className="text-blue-600 font-medium text-sm">Settings</Link>
        </div>
      </div>
    </header>
  );
}
