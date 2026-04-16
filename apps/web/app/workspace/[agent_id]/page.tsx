"use client";

import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  MessageSquare,
  Terminal,
  Globe,
  FileText,
  GitBranch,
  Send,
  Play,
  RefreshCw,
  Loader2,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Tab = "chat" | "terminal" | "browser" | "files" | "git";

interface TaskLog {
  id: string;
  description: string;
  status: string;
  success?: boolean;
  result_data?: any;
  created_at: string;
}

interface AgentInfo {
  id: string;
  agent_id: string;
  name: string;
  role: string;
  status: string;
  level: number;
}

export default function AgentWorkspace() {
  const { agent_id } = useParams<{ agent_id: string }>();
  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [agent, setAgent] = useState<AgentInfo | null>(null);
  const [tasks, setTasks] = useState<TaskLog[]>([]);
  const [loading, setLoading] = useState(true);

  // Chat
  const [messages, setMessages] = useState<{ role: "user" | "agent"; text: string }[]>([
    { role: "agent", text: "Hello! I'm ready to work. What task should I handle?" },
  ]);
  const [input, setInput] = useState("");

  // Terminal
  const [terminalLines, setTerminalLines] = useState<string[]>([
    "$ agent initialized",
    `$ workspace: /agents/${agent_id}`,
  ]);
  const [terminalInput, setTerminalInput] = useState("");

  // Browser
  const [browserUrl, setBrowserUrl] = useState("https://example.com");
  const [browserContent, setBrowserContent] = useState("");
  const [browserLoading, setBrowserLoading] = useState(false);

  // Files
  const [filePath, setFilePath] = useState("");
  const [fileContent, setFileContent] = useState("");

  useEffect(() => {
    fetchWorkspace();
  }, [agent_id]);

  const fetchWorkspace = async () => {
    try {
      const res = await fetch(`${API_URL}/workspaces/agents/${agent_id}`);
      const data = await res.json();
      setAgent(data.agent);
      setTasks(data.tasks || []);
    } catch (e) {
      console.error("Failed to load workspace");
    } finally {
      setLoading(false);
    }
  };

  const sendChat = async () => {
    if (!input.trim()) return;
    setMessages((m) => [...m, { role: "user", text: input }]);
    const currentInput = input;
    setInput("");

    // In a real implementation this would queue a task to the agent
    setTimeout(() => {
      setMessages((m) => [
        ...m,
        { role: "agent", text: `Received task: "${currentInput}". I'll process this in the background.` },
      ]);
    }, 500);
  };

  const runTerminalCommand = async () => {
    if (!terminalInput.trim()) return;
    setTerminalLines((l) => [...l, `$ ${terminalInput}`]);
    const cmd = terminalInput;
    setTerminalInput("");

    try {
      const res = await fetch(`${API_URL}/workspaces/agents/${agent_id}/terminal?command=${encodeURIComponent(cmd)}`, {
        method: "POST",
      });
      const data = await res.json();
      if (data.stdout) setTerminalLines((l) => [...l, data.stdout]);
      if (data.stderr) setTerminalLines((l) => [...l, `stderr: ${data.stderr}`]);
      if (data.error) setTerminalLines((l) => [...l, `error: ${data.error}`]);
    } catch (e) {
      setTerminalLines((l) => [...l, `error: ${e}`]);
    }
  };

  const navigateBrowser = async () => {
    setBrowserLoading(true);
    try {
      const res = await fetch(`${API_URL}/workspaces/agents/${agent_id}/browser/navigate?url=${encodeURIComponent(browserUrl)}`, {
        method: "POST",
      });
      const data = await res.json();
      if (data.success) {
        // Then fetch snapshot
        const snapRes = await fetch(`${API_URL}/workspaces/agents/${agent_id}/browser/snapshot`, { method: "POST" });
        const snapData = await snapRes.json();
        setBrowserContent(snapData.content || "Page loaded. No content extracted.");
      } else {
        setBrowserContent(`Error: ${data.error}`);
      }
    } catch (e) {
      setBrowserContent(`Error: ${e}`);
    } finally {
      setBrowserLoading(false);
    }
  };

  const readFile = async () => {
    if (!filePath.trim()) return;
    try {
      const res = await fetch(`${API_URL}/workspaces/agents/${agent_id}/files/read?path=${encodeURIComponent(filePath)}`, {
        method: "POST",
      });
      const data = await res.json();
      setFileContent(data.content || data.error || "No content");
    } catch (e) {
      setFileContent(`Error: ${e}`);
    }
  };

  const writeFile = async () => {
    if (!filePath.trim()) return;
    try {
      const res = await fetch(`${API_URL}/workspaces/agents/${agent_id}/files/write`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: filePath, content: fileContent }),
      });
      const data = await res.json();
      alert(data.success ? "File saved" : `Error: ${data.error}`);
    } catch (e) {
      alert(`Error: ${e}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
              <span className="text-lg font-bold">ARLI</span>
            </Link>
            {agent && (
              <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600">
                <span className="font-semibold text-gray-900">{agent.name}</span>
                <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">{agent.role}</span>
                <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded text-xs">Lv.{agent.level}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchWorkspace}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-gray-100 rounded-lg transition"
              title="Refresh"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 flex gap-1">
          {[
            { id: "chat", label: "Chat", icon: MessageSquare },
            { id: "terminal", label: "Terminal", icon: Terminal },
            { id: "browser", label: "Browser", icon: Globe },
            { id: "files", label: "Files", icon: FileText },
            { id: "git", label: "Git", icon: GitBranch },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as Tab)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition ${
                activeTab === t.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
              }`}
            >
              <t.icon className="w-4 h-4" />
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-4">
        {activeTab === "chat" && (
          <div className="bg-white rounded-xl shadow-sm border h-[calc(100vh-180px)] flex flex-col">
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-xl px-4 py-2 rounded-lg text-sm ${
                      m.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    {m.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="border-t p-3 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendChat()}
                placeholder="Type a task..."
                className="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={sendChat}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Send
              </button>
            </div>
          </div>
        )}

        {activeTab === "terminal" && (
          <div className="bg-gray-900 rounded-xl shadow-sm border h-[calc(100vh-180px)] flex flex-col text-gray-100 font-mono text-sm">
            <div className="flex-1 overflow-y-auto p-4 space-y-1">
              {terminalLines.map((line, i) => (
                <div key={i} className="whitespace-pre-wrap">{line}</div>
              ))}
            </div>
            <div className="border-t border-gray-700 p-3 flex gap-2">
              <span className="text-green-400 py-2">$</span>
              <input
                type="text"
                value={terminalInput}
                onChange={(e) => setTerminalInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && runTerminalCommand()}
                placeholder="Enter command..."
                className="flex-1 bg-transparent outline-none text-gray-100 font-mono"
              />
              <button onClick={runTerminalCommand} className="text-gray-400 hover:text-white">
                <Play className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {activeTab === "browser" && (
          <div className="bg-white rounded-xl shadow-sm border h-[calc(100vh-180px)] flex flex-col">
            <div className="border-b p-3 flex gap-2">
              <input
                type="text"
                value={browserUrl}
                onChange={(e) => setBrowserUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && navigateBrowser()}
                className="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={navigateBrowser}
                disabled={browserLoading}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                {browserLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Navigate"}
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4 bg-gray-50">
              {browserContent ? (
                <pre className="text-xs text-gray-700 whitespace-pre-wrap">{browserContent}</pre>
              ) : (
                <div className="text-gray-400 text-sm">Enter a URL and click Navigate to start browsing.</div>
              )}
            </div>
          </div>
        )}

        {activeTab === "files" && (
          <div className="bg-white rounded-xl shadow-sm border h-[calc(100vh-180px)] flex flex-col">
            <div className="border-b p-3 flex gap-2">
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="path/to/file.py"
                className="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button onClick={readFile} className="px-4 py-2 border rounded-lg hover:bg-gray-50 text-sm">
                Read
              </button>
              <button onClick={writeFile} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                Save
              </button>
            </div>
            <textarea
              value={fileContent}
              onChange={(e) => setFileContent(e.target.value)}
              className="flex-1 p-4 font-mono text-sm outline-none resize-none"
              placeholder="File content will appear here..."
            />
          </div>
        )}

        {activeTab === "git" && (
          <div className="bg-white rounded-xl shadow-sm border h-[calc(100vh-180px)] flex flex-col p-4">
            <h3 className="font-semibold mb-4">Git Status</h3>
            <div className="text-sm text-gray-600 mb-4">
              Git integration is managed via the Terminal tab. Run commands like:
            </div>
            <div className="bg-gray-900 text-gray-100 font-mono text-sm p-4 rounded-lg space-y-1">
              <div>$ git status</div>
              <div>$ git add .</div>
              <div>$ git commit -m "agent update"</div>
              <div>$ git push</div>
            </div>
          </div>
        )}
      </main>

      {/* Task History Sidebar (bottom on mobile, right on desktop) */}
      <aside className="bg-white border-t lg:border-t-0 lg:border-l lg:fixed lg:right-0 lg:top-28 lg:bottom-0 lg:w-80 overflow-y-auto">
        <div className="p-4">
          <h3 className="font-semibold text-gray-900 mb-3">Recent Tasks</h3>
          <div className="space-y-2">
            {tasks.length === 0 && <div className="text-sm text-gray-500">No tasks yet</div>}
            {tasks.map((t) => (
              <div key={t.id} className="text-sm border rounded-lg p-3 hover:bg-gray-50">
                <div className="font-medium truncate">{t.description}</div>
                <div className="flex items-center gap-2 mt-1">
                  <StatusBadge status={t.status} />
                  {t.success != null && (
                    <span className={`text-xs ${t.success ? "text-green-600" : "text-red-600"}`}>
                      {t.success ? "✓" : "✗"}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-gray-100 text-gray-700",
    running: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
    queued: "bg-yellow-100 text-yellow-700",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded ${colors[status] || colors.pending}`}>
      {status}
    </span>
  );
}
