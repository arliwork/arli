"use client";

import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Terminal,
  Globe,
  FolderOpen,
  GitBranch,
  MessageSquare,
  Send,
  Play,
  RefreshCw,
  Search,
  ChevronRight,
  Loader2,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Tab = "chat" | "terminal" | "browser" | "files" | "git";

interface LogEntry {
  timestamp: string;
  agent: string;
  action: string;
  details: string;
}

interface TaskResult {
  role?: string;
  output?: string;
  success?: boolean;
  credits_used?: number;
  model_used?: string;
  error?: string;
}

export default function Workspace() {
  const searchParams = useSearchParams();
  const workflowId = searchParams.get("workflow") || "";
  const taskId = searchParams.get("task") || "";

  const [activeTab, setActiveTab] = useState<Tab>("chat");
  const [agentRole, setAgentRole] = useState<string>("backend-dev");
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<{role: string; content: string}[]>([]);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);
  const [browserUrl, setBrowserUrl] = useState("https://example.com");
  const [browserContent, setBrowserContent] = useState<any>(null);
  const [files, setFiles] = useState<string[]>(["src/main.py", "src/config.py", "README.md"]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [taskResult, setTaskResult] = useState<TaskResult | null>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (workflowId) {
      addLog("System", `Loaded workflow: ${workflowId}`);
    }
    if (taskId) {
      addLog("System", `Task ID: ${taskId}`);
    }
  }, [workflowId, taskId]);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [terminalLogs]);

  const addLog = (action: string, details: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setTerminalLogs((prev) => [...prev, `[${timestamp}] [${action}] ${details}`]);
  };

  const runAgentTask = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: prompt }]);
    addLog("User", prompt);

    try {
      // Call the execute-task API with real LLM + runtime
      const res = await fetch(`${API_URL}/orchestration/execute-task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          role: agentRole,
          description: prompt,
          workflow_id: workflowId || undefined,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      setTaskResult(data);
      
      const output = data.output || data.error || "No output";
      setMessages((prev) => [...prev, { role: "assistant", content: output }]);
      addLog(agentRole, output.substring(0, 200));
    } catch (e: any) {
      const errorMsg = `Error: ${e.message}`;
      setMessages((prev) => [...prev, { role: "assistant", content: errorMsg }]);
      addLog("Error", e.message);
    } finally {
      setLoading(false);
      setPrompt("");
    }
  };

  const runBrowserExtract = async () => {
    setLoading(true);
    addLog("Browser", `Navigating to ${browserUrl}`);
    try {
      const res = await fetch(`${API_URL}/agents/run-browser-extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: browserUrl }),
      });
      const data = await res.json();
      setBrowserContent(data);
      addLog("Browser", `Extracted ${data.title || "page"} (${data.content_length || 0} chars)`);
    } catch (e: any) {
      addLog("Browser Error", e.message);
    } finally {
      setLoading(false);
    }
  };

  const runBrowserSearch = async () => {
    setLoading(true);
    addLog("Browser", `Searching: ${prompt}`);
    try {
      const res = await fetch(`${API_URL}/agents/run-browser-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: prompt }),
      });
      const data = await res.json();
      setBrowserContent(data);
      addLog("Browser", `Found ${data.count || 0} results`);
    } catch (e: any) {
      addLog("Browser Error", e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
              <span className="text-lg font-bold">ARLI</span>
            </Link>
            <span className="text-gray-300">|</span>
            <span className="font-semibold text-gray-700">Agent Workspace</span>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={agentRole}
              onChange={(e) => setAgentRole(e.target.value)}
              className="border rounded px-3 py-1.5 text-sm"
            >
              <option value="ceo">CEO</option>
              <option value="architect">Architect</option>
              <option value="backend-dev">Backend Dev</option>
              <option value="frontend-dev">Frontend Dev</option>
              <option value="devops">DevOps</option>
              <option value="researcher">Researcher</option>
            </select>
            <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900">Dashboard</Link>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex max-w-7xl mx-auto w-full">
        {/* Sidebar Tabs */}
        <div className="w-16 bg-white border-r flex flex-col items-center py-4 gap-2">
          <TabButton icon={<MessageSquare className="w-5 h-5" />} label="Chat" active={activeTab === "chat"} onClick={() => setActiveTab("chat")} />
          <TabButton icon={<Terminal className="w-5 h-5" />} label="Terminal" active={activeTab === "terminal"} onClick={() => setActiveTab("terminal")} />
          <TabButton icon={<Globe className="w-5 h-5" />} label="Browser" active={activeTab === "browser"} onClick={() => setActiveTab("browser")} />
          <TabButton icon={<FolderOpen className="w-5 h-5" />} label="Files" active={activeTab === "files"} onClick={() => setActiveTab("files")} />
          <TabButton icon={<GitBranch className="w-5 h-5" />} label="Git" active={activeTab === "git"} onClick={() => setActiveTab("git")} />
        </div>

        {/* Content Area */}
        <div className="flex-1 flex flex-col min-h-[calc(100vh-3.5rem)]">
          {activeTab === "chat" && (
            <div className="flex-1 flex flex-col">
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-400 mt-12">
                    <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p className="text-lg">Start a conversation with your agent</p>
                    <p className="text-sm mt-1">Ask them to write code, research, plan, or execute tasks</p>
                  </div>
                )}
                {messages.map((m, i) => (
                  <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-2xl px-4 py-3 rounded-lg ${m.role === "user" ? "bg-blue-600 text-white" : "bg-white border shadow-sm"}`}>
                      <div className="text-xs font-semibold mb-1 opacity-70">{m.role}</div>
                      <div className="whitespace-pre-wrap text-sm">{m.content}</div>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white border shadow-sm px-4 py-3 rounded-lg flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm text-gray-600">Agent is thinking...</span>
                    </div>
                  </div>
                )}
              </div>
              <div className="border-t bg-white p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && runAgentTask()}
                    placeholder={`Ask ${agentRole} to do something...`}
                    className="flex-1 border rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                  <button
                    onClick={runAgentTask}
                    disabled={loading || !prompt.trim()}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    Send
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "terminal" && (
            <div className="flex-1 bg-gray-900 text-green-400 font-mono text-sm p-4 overflow-y-auto">
              {terminalLogs.length === 0 && <div className="text-gray-500">No activity yet. Run a task to see live logs.</div>}
              {terminalLogs.map((log, i) => (
                <div key={i} className="py-0.5">{log}</div>
              ))}
              <div ref={terminalEndRef} />
            </div>
          )}

          {activeTab === "browser" && (
            <div className="flex-1 flex flex-col p-4 gap-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={browserUrl}
                  onChange={(e) => setBrowserUrl(e.target.value)}
                  className="flex-1 border rounded-lg px-4 py-2"
                  placeholder="https://..."
                />
                <button onClick={runBrowserExtract} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2">
                  <Globe className="w-4 h-4" /> Extract
                </button>
                <button onClick={runBrowserSearch} disabled={loading} className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50 flex items-center gap-2">
                  <Search className="w-4 h-4" /> Search
                </button>
              </div>
              
              <div className="flex-1 bg-white border rounded-lg p-4 overflow-y-auto">
                {!browserContent && <div className="text-gray-400 text-center mt-12">Enter a URL or search query to see results</div>}
                {browserContent?.title && (
                  <div className="mb-4">
                    <h3 className="text-xl font-bold">{browserContent.title}</h3>
                    <a href={browserContent.url} target="_blank" rel="noreferrer" className="text-blue-600 text-sm">{browserContent.url}</a>
                  </div>
                )}
                {browserContent?.text_preview && (
                  <div className="text-sm text-gray-700 whitespace-pre-wrap">{browserContent.text_full || browserContent.text_preview}</div>
                )}
                {browserContent?.results && (
                  <div className="space-y-3">
                    {browserContent.results.map((r: any, i: number) => (
                      <div key={i} className="border-b pb-2">
                        <a href={r.url} target="_blank" rel="noreferrer" className="text-blue-600 font-medium hover:underline">{r.title}</a>
                        <div className="text-xs text-gray-500">{r.url}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "files" && (
            <div className="flex-1 flex">
              <div className="w-64 bg-white border-r p-4">
                <h3 className="font-semibold mb-3">Files</h3>
                <div className="space-y-1">
                  {files.map((f) => (
                    <button
                      key={f}
                      onClick={() => { setSelectedFile(f); setFileContent(`# ${f}\n\n# File content would be loaded from agent workspace`); }}
                      className={`w-full text-left px-3 py-2 rounded text-sm ${selectedFile === f ? "bg-blue-50 text-blue-700" : "hover:bg-gray-100"}`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex-1 p-4">
                {selectedFile ? (
                  <div>
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="font-semibold">{selectedFile}</h3>
                      <button className="text-sm bg-blue-600 text-white px-3 py-1 rounded">Save</button>
                    </div>
                    <textarea
                      value={fileContent}
                      onChange={(e) => setFileContent(e.target.value)}
                      className="w-full h-[calc(100vh-12rem)] border rounded-lg p-4 font-mono text-sm"
                    />
                  </div>
                ) : (
                  <div className="text-gray-400 text-center mt-12">Select a file to view and edit</div>
                )}
              </div>
            </div>
          )}

          {activeTab === "git" && (
            <div className="flex-1 p-4">
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-semibold mb-4">Git Status</h3>
                <div className="font-mono text-sm text-gray-700 space-y-2">
                  <div>$ git status</div>
                  <div className="text-green-600">On branch main</div>
                  <div className="text-gray-500">Your branch is up to date with origin/main.</div>
                  <div className="mt-2">nothing to commit, working tree clean</div>
                </div>
                <div className="mt-6 flex gap-2">
                  <button className="border px-4 py-2 rounded hover:bg-gray-50">Pull</button>
                  <button className="border px-4 py-2 rounded hover:bg-gray-50">Commit</button>
                  <button className="border px-4 py-2 rounded hover:bg-gray-50">Push</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function TabButton({ icon, label, active, onClick }: { icon: React.ReactNode; label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`flex flex-col items-center gap-1 p-2 rounded-lg transition w-14 ${active ? "bg-blue-50 text-blue-600" : "text-gray-500 hover:bg-gray-100"}`}
    >
      {icon}
      <span className="text-[10px] font-medium">{label}</span>
    </button>
  );
}
