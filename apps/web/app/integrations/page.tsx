"use client";

import { useState } from "react";
import Link from "next/link";
import { MessageSquare, Copy, CheckCircle, Terminal, Globe } from "lucide-react";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function IntegrationsPage() {
  const [copied, setCopied] = useState(false);
  const webhookUrl = `${API_URL}/webhooks/telegram`;

  const copyWebhook = () => {
    navigator.clipboard.writeText(webhookUrl);
    setCopied(true);
    toast.success("Webhook URL copied");
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <span className="text-lg font-bold">ARLI</span>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
            <Link href="/templates" className="text-gray-600 hover:text-gray-900">Templates</Link>
            <Link href="/workspace" className="text-gray-600 hover:text-gray-900">Workspace</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Integrations</h1>
        <p className="text-gray-600 mb-8">Connect ARLI agents to your favorite channels and platforms.</p>

        {/* Telegram */}
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Telegram</h2>
              <p className="text-sm text-gray-600">Chat with your ARLI agents directly in Telegram.</p>
            </div>
            <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Active</span>
          </div>

          <div className="bg-gray-900 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Webhook URL</span>
              <button onClick={copyWebhook} className="text-gray-400 hover:text-white transition">
                {copied ? <CheckCircle className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
            <code className="text-green-400 text-sm break-all">{webhookUrl}</code>
          </div>

          <div className="space-y-2 text-sm text-gray-700">
            <p className="font-medium">Setup instructions:</p>
            <ol className="list-decimal list-inside space-y-1 text-gray-600">
              <li>Create a Telegram bot with <a href="https://t.me/BotFather" className="text-blue-600 hover:underline" target="_blank" rel="noreferrer">@BotFather</a></li>
              <li>Copy your bot token to <code className="bg-gray-100 px-1 rounded">apps/api/.env</code> as <code className="bg-gray-100 px-1 rounded">TELEGRAM_BOT_TOKEN</code></li>
              <li>Set the webhook: <code className="bg-gray-100 px-1 rounded text-xs">curl -X POST https://api.telegram.org/bot&lt;TOKEN&gt;/setWebhook -d url={webhookUrl}</code></li>
              <li>Start chatting with your bot!</li>
            </ol>
          </div>

          <div className="mt-4 border-t pt-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Supported commands:</p>
            <div className="grid sm:grid-cols-2 gap-2 text-sm text-gray-600">
              <div className="bg-gray-50 rounded px-3 py-2"><code>/start</code> \u2014 Welcome message</div>
              <div className="bg-gray-50 rounded px-3 py-2"><code>/agents</code> \u2014 List your agents</div>
              <div className="bg-gray-50 rounded px-3 py-2"><code>/status</code> \u2014 Platform status</div>
              <div className="bg-gray-50 rounded px-3 py-2"><code>/balance</code> \u2014 Credit balance</div>
              <div className="bg-gray-50 rounded px-3 py-2 sm:col-span-2">Any other message \u2192 creates a task for AI execution</div>
            </div>
          </div>
        </div>

        {/* Browser Automation */}
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Globe className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Browser Automation</h2>
              <p className="text-sm text-gray-600">Agents can navigate websites, fill forms, and scrape data.</p>
            </div>
            <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Active</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Use the <Link href="/workspace" className="text-blue-600 hover:underline">Workspace</Link> Browser tab to control agent browsing sessions in real time.
          </p>
        </div>

        {/* Terminal */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <Terminal className="w-5 h-5 text-gray-700" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Terminal Access</h2>
              <p className="text-sm text-gray-600">Agents execute real shell commands in their workspace.</p>
            </div>
            <span className="ml-auto text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">Active</span>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Available in every agent workspace. Commands run sandboxed in the agent\u2019s working directory.
          </p>
        </div>
      </main>
    </div>
  );
}
