"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type DemoStep = "welcome" | "creating" | "team" | "strategy" | "approving" | "executing" | "running" | "complete";

interface DemoAgent {
  agent_id: string;
  name: string;
  role: string;
  description?: string;
}

interface DemoCompany {
  company_id: string;
  company_name: string;
  goal: string;
  ceo_id: string;
  team: DemoAgent[];
}

interface StrategyPhase {
  phase_name: string;
  duration_days: number;
  tasks: string[];
}

interface Strategy {
  strategy_summary: string;
  key_objectives: string[];
  recommended_team: { role: string; reason: string; budget: number }[];
  phases: StrategyPhase[];
  success_metrics: string[];
}

interface ConsoleLog {
  id: string;
  timestamp: string;
  agent: string;
  role: string;
  message: string;
  type: "info" | "action" | "success" | "warning" | "revenue";
}

const PRESETS = [
  { label: "Crypto Trading Firm", goal: "Build an automated crypto trading and analysis firm" },
  { label: "Content Agency", goal: "Launch a viral content creation agency for TikTok and Instagram" },
  { label: "SaaS Builder", goal: "Create a micro-SaaS product for small business automation" },
  { label: "Research Lab", goal: "Build an AI research lab that produces market intelligence reports" },
];

export default function DemoPage() {
  const router = useRouter();
  const [step, setStep] = useState<DemoStep>("welcome");
  const [goal, setGoal] = useState("");
  const [company, setCompany] = useState<DemoCompany | null>(null);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [approvalId, setApprovalId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<string[]>([]);
  const [logs, setLogs] = useState<ConsoleLog[]>([]);
  const [running, setRunning] = useState(false);
  const [stats, setStats] = useState({ revenue: 0, tasksDone: 0, cycles: 0 });
  const consoleEndRef = useRef<HTMLDivElement | null>(null);

  const addLog = useCallback((agent: string, role: string, message: string, type: ConsoleLog["type"] = "info") => {
    const log: ConsoleLog = {
      id: Math.random().toString(36).slice(2),
      timestamp: new Date().toLocaleTimeString(),
      agent,
      role,
      message,
      type,
    };
    setLogs((prev) => [...prev.slice(-50), log]);
  }, []);

  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const apiPost = async (path: string, params?: Record<string, string>) => {
    const url = new URL(`${API_URL}${path}`);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    }
    const res = await fetch(url.toString(), {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }
    return res.json();
  };

  const startDemo = async () => {
    if (!goal.trim()) {
      toast.error("Enter a goal first");
      return;
    }
    setStep("creating");
    setLogs([]);
    addLog("System", "system", `Initializing autonomous company creation for: "${goal}"`, "info");

    try {
      addLog("AI Architect", "orchestrator", "Analyzing market opportunity and optimal team composition...", "action");
      await new Promise((r) => setTimeout(r, 1500));

      const data = await apiPost("/autonomous/demo/create-company", { goal });
      setCompany(data);
      addLog("AI Architect", "orchestrator", `Company "${data.company_name}" created with ${data.team.length} agents`, "success");

      setStep("team");
      await new Promise((r) => setTimeout(r, 1200));

      // Auto-advance to strategy after showing team
      setStep("strategy");
      addLog(data.team.find((a: DemoAgent) => a.role === "ceo")?.name || "CEO", "ceo", "Received company goal. Generating strategic plan...", "action");

      const ceoId = data.team.find((a: DemoAgent) => a.role === "ceo")?.agent_id || data.ceo_id;
      const stratData = await apiPost("/autonomous/strategy/generate", {
        company_id: data.company_id,
        ceo_agent_id: ceoId,
      });

      setStrategy(stratData.strategy);
      setApprovalId(stratData.approval_id);
      addLog(stratData.strategy?.key_objectives?.[0] ? "CEO" : "CEO", "ceo", `Strategy generated: ${stratData.approval_id}`, "success");
    } catch (e: any) {
      toast.error(e.message || "Demo failed");
      setStep("welcome");
    }
  };

  const approveStrategy = async () => {
    if (!approvalId) return;
    setStep("approving");
    addLog("User", "admin", `Approving strategy ${approvalId}...`, "action");

    try {
      // Call approvals endpoint to approve
      await fetch(`${API_URL}/approvals/${approvalId}/approve`, {
        method: "POST",
        credentials: "include",
      });

      const execData = await apiPost("/autonomous/strategy/execute", { approval_id: approvalId });
      setTasks(execData.task_descriptions || []);
      addLog("System", "system", `Strategy approved. ${execData.tasks_created} tasks created and assigned.`, "success");
      setStep("executing");
    } catch (e: any) {
      toast.error(e.message || "Execution failed");
    }
  };

  const runCycle = async () => {
    setRunning(true);
    setStep("running");
    addLog("System", "system", "Starting heartbeat cycle...", "action");

    try {
      const cycleData = await apiPost("/autonomous/demo/run-cycle");
      setStats((s) => ({
        revenue: s.revenue + Math.floor(Math.random() * 500) + 100,
        tasksDone: s.tasksDone + (cycleData.agents_processed || 0),
        cycles: s.cycles + 1,
      }));

      (cycleData.results || []).forEach((r: any, i: number) => {
        setTimeout(() => {
          if (r.error) {
            addLog(r.name || "Agent", r.role || "agent", `Error: ${r.error}`, "warning");
          } else {
            const action = r.outcome?.decision?.action || "heartbeat";
            addLog(r.name || "Agent", r.role || "agent", `Executed: ${action}`, action === "idle" ? "info" : "success");
            if (action !== "idle") {
              addLog("System", "system", `+$${Math.floor(Math.random() * 200 + 50)} revenue generated`, "revenue");
            }
          }
        }, i * 400);
      });

      setTimeout(() => {
        setStep("complete");
        addLog("System", "system", "Heartbeat cycle complete. Company is operational.", "success");
        setRunning(false);
      }, ((cycleData.results || []).length * 400) + 500);
    } catch (e: any) {
      toast.error(e.message || "Cycle failed");
      setRunning(false);
    }
  };

  const resetDemo = () => {
    setStep("welcome");
    setGoal("");
    setCompany(null);
    setStrategy(null);
    setApprovalId(null);
    setTasks([]);
    setLogs([]);
    setStats({ revenue: 0, tasksDone: 0, cycles: 0 });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <span className="text-lg font-bold">ARLI Demo</span>
          </Link>
          <div className="flex items-center gap-3">
            <StepIndicator step={step} />
            <button onClick={resetDemo} className="text-xs text-slate-400 hover:text-white transition">Reset</button>
            <Link href="/dashboard" className="text-xs text-blue-400 hover:text-blue-300 transition">Dashboard →</Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
        {step === "welcome" && (
          <WelcomeStep goal={goal} setGoal={setGoal} onStart={startDemo} presets={PRESETS} />
        )}
        {step === "creating" && <CreatingStep goal={goal} />}
        {step === "team" && company && <TeamStep company={company} />}
        {step === "strategy" && company && strategy && (
          <StrategyStep strategy={strategy} company={company} onApprove={approveStrategy} />
        )}
        {step === "approving" && <ApprovingStep />}
        {step === "executing" && company && (
          <ExecutingStep company={company} tasks={tasks} onRunCycle={runCycle} running={running} />
        )}
        {step === "running" && <RunningStep logs={logs} />}
        {step === "complete" && (
          <CompleteStep stats={stats} company={company} onReset={resetDemo} />
        )}
      </main>

      {/* Console */}
      <DemoConsole logs={logs} consoleEndRef={consoleEndRef} />
    </div>
  );
}

/* ─── Sub-components ─── */

function StepIndicator({ step }: { step: DemoStep }) {
  const steps: DemoStep[] = ["welcome", "creating", "team", "strategy", "executing", "running", "complete"];
  const idx = steps.indexOf(step);
  return (
    <div className="flex items-center gap-1">
      {steps.map((s, i) => (
        <div key={s} className={`w-2 h-2 rounded-full ${i <= idx ? "bg-blue-500" : "bg-slate-700"}`} />
      ))}
    </div>
  );
}

function WelcomeStep({ goal, setGoal, onStart, presets }: {
  goal: string; setGoal: (g: string) => void; onStart: () => void; presets: typeof PRESETS;
}) {
  return (
    <div className="max-w-2xl mx-auto text-center pt-12">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm mb-6 border border-blue-500/20">
        <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
        Autonomous AI Company Demo
      </div>
      <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white via-blue-200 to-blue-400 bg-clip-text text-transparent">
        Watch AI Build a Company in 60 Seconds
      </h1>
      <p className="text-slate-400 text-lg mb-10">
        Enter any business goal. Our AI CEO will assemble a team, create a strategy, and start executing — automatically.
      </p>

      <div className="flex gap-3 mb-8">
        <input
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onStart()}
          placeholder="e.g. Build a crypto trading analysis firm..."
          className="flex-1 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 outline-none focus:border-blue-500 transition"
        />
        <button
          onClick={onStart}
          disabled={!goal.trim()}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition"
        >
          Start Demo →
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {presets.map((p) => (
          <button
            key={p.label}
            onClick={() => setGoal(p.goal)}
            className={`p-3 rounded-xl border text-left transition ${
              goal === p.goal ? "border-blue-500 bg-blue-500/10" : "border-slate-700 bg-slate-900 hover:border-slate-600"
            }`}
          >
            <div className="text-sm font-medium text-white">{p.label}</div>
            <div className="text-xs text-slate-500 mt-1 truncate">{p.goal}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

function CreatingStep({ goal }: { goal: string }) {
  return (
    <div className="max-w-xl mx-auto text-center pt-20">
      <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-6" />
      <h2 className="text-2xl font-bold mb-2">Designing Your Company</h2>
      <p className="text-slate-400 mb-8">AI Architect is analyzing the market and assembling the optimal team...</p>
      <div className="bg-slate-900 rounded-xl p-4 border border-slate-800 text-left font-mono text-sm text-slate-300 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-green-500">✓</span> Analyzing goal: {goal.slice(0, 60)}...
        </div>
        <div className="flex items-center gap-2">
          <span className="text-green-500">✓</span> Market opportunity assessment
        </div>
        <div className="flex items-center gap-2 animate-pulse">
          <span className="text-blue-500">⟳</span> Optimal team composition
        </div>
        <div className="flex items-center gap-2 text-slate-600">
          <span>○</span> Creating agents and assigning roles
        </div>
        <div className="flex items-center gap-2 text-slate-600">
          <span>○</span> Initializing CEO with strategic directive
        </div>
      </div>
    </div>
  );
}

function TeamStep({ company }: { company: DemoCompany }) {
  return (
    <div className="max-w-3xl mx-auto pt-8">
      <h2 className="text-2xl font-bold mb-2 text-center">Team Assembled</h2>
      <p className="text-slate-400 text-center mb-8">{company.company_name} — {company.goal}</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {company.team.map((agent, i) => (
          <div
            key={agent.agent_id}
            className="bg-slate-900 border border-slate-700 rounded-xl p-5 hover:border-blue-500/50 transition"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                {agent.name.charAt(0)}
              </div>
              <div>
                <div className="font-semibold text-white">{agent.name}</div>
                <div className="text-xs text-blue-400 uppercase tracking-wide">{agent.role}</div>
              </div>
            </div>
            <p className="text-sm text-slate-400">{agent.description || `Responsible for ${agent.role} operations`}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function StrategyStep({ strategy, company, onApprove }: {
  strategy: Strategy; company: DemoCompany; onApprove: () => void;
}) {
  return (
    <div className="max-w-3xl mx-auto pt-8">
      <h2 className="text-2xl font-bold mb-2 text-center">CEO Strategy</h2>
      <p className="text-slate-400 text-center mb-8">{company.team.find((a) => a.role === "ceo")?.name} has proposed the following strategy</p>

      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 mb-6">
        <h3 className="text-lg font-semibold text-blue-400 mb-3">Overview</h3>
        <p className="text-slate-300 mb-6">{strategy.strategy_summary}</p>

        <h3 className="text-lg font-semibold text-blue-400 mb-3">Key Objectives</h3>
        <div className="space-y-2 mb-6">
          {strategy.key_objectives?.map((obj, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-blue-500 mt-1">▸</span>
              <span className="text-slate-300">{obj}</span>
            </div>
          )) || <p className="text-slate-500">No objectives listed</p>}
        </div>

        <h3 className="text-lg font-semibold text-blue-400 mb-3">Execution Phases</h3>
        <div className="space-y-3 mb-6">
          {strategy.phases?.map((phase, i) => (
            <div key={i} className="bg-slate-800/50 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-white">{phase.phase_name}</span>
                <span className="text-xs text-slate-500">{phase.duration_days} days</span>
              </div>
              <div className="text-sm text-slate-400">
                {phase.tasks?.join(" → ")}
              </div>
            </div>
          )) || <p className="text-slate-500">No phases defined</p>}
        </div>

        <h3 className="text-lg font-semibold text-blue-400 mb-3">Success Metrics</h3>
        <div className="flex flex-wrap gap-2">
          {strategy.success_metrics?.map((m, i) => (
            <span key={i} className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 text-sm border border-blue-500/20">
              {m}
            </span>
          )) || <span className="text-slate-500">No metrics defined</span>}
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={onApprove}
          className="bg-green-600 hover:bg-green-500 text-white px-8 py-3 rounded-xl font-medium transition text-lg"
        >
          ✓ Approve Strategy & Execute
        </button>
      </div>
    </div>
  );
}

function ApprovingStep() {
  return (
    <div className="max-w-xl mx-auto text-center pt-20">
      <div className="w-16 h-16 border-4 border-green-500/30 border-t-green-500 rounded-full animate-spin mx-auto mb-6" />
      <h2 className="text-2xl font-bold mb-2">Approving & Deploying</h2>
      <p className="text-slate-400">Decomposing strategy into actionable tasks and assigning to team members...</p>
    </div>
  );
}

function ExecutingStep({ company, tasks, onRunCycle, running }: {
  company: DemoCompany; tasks: string[]; onRunCycle: () => void; running: boolean;
}) {
  return (
    <div className="max-w-3xl mx-auto pt-8">
      <h2 className="text-2xl font-bold mb-2 text-center">Tasks Deployed</h2>
      <p className="text-slate-400 text-center mb-8">{tasks.length} tasks created and assigned to {company.team.length} agents</p>

      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 mb-6">
        <div className="space-y-3">
          {tasks.map((task, i) => (
            <div key={i} className="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3">
              <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-sm font-bold">
                {i + 1}
              </div>
              <span className="text-slate-300">{task}</span>
            </div>
          ))}
          {tasks.length === 0 && (
            <p className="text-slate-500 text-center py-4">No tasks generated yet</p>
          )}
        </div>
      </div>

      <div className="flex justify-center">
        <button
          onClick={onRunCycle}
          disabled={running}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-8 py-3 rounded-xl font-medium transition text-lg"
        >
          {running ? "Running Cycle..." : "▶ Run Heartbeat Cycle"}
        </button>
      </div>
    </div>
  );
}

function RunningStep({ logs }: { logs: ConsoleLog[] }) {
  return (
    <div className="max-w-3xl mx-auto pt-8 text-center">
      <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto mb-6" />
      <h2 className="text-2xl font-bold mb-2">Agents at Work</h2>
      <p className="text-slate-400">Heartbeat cycle in progress. Watch the console below for live agent activity.</p>
    </div>
  );
}

function CompleteStep({ stats, company, onReset }: {
  stats: { revenue: number; tasksDone: number; cycles: number };
  company: DemoCompany | null;
  onReset: () => void;
}) {
  return (
    <div className="max-w-2xl mx-auto pt-8 text-center">
      <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
        <span className="text-4xl">🎉</span>
      </div>
      <h2 className="text-3xl font-bold mb-2">Company is Operational!</h2>
      <p className="text-slate-400 mb-10">{company?.company_name || "Your AI company"} is now running autonomously.</p>

      <div className="grid grid-cols-3 gap-4 mb-10">
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
          <div className="text-3xl font-bold text-green-400">${stats.revenue.toLocaleString()}</div>
          <div className="text-sm text-slate-500 mt-1">Revenue Generated</div>
        </div>
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
          <div className="text-3xl font-bold text-blue-400">{stats.tasksDone}</div>
          <div className="text-sm text-slate-500 mt-1">Actions Executed</div>
        </div>
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5">
          <div className="text-3xl font-bold text-purple-400">{stats.cycles}</div>
          <div className="text-sm text-slate-500 mt-1">Cycles Completed</div>
        </div>
      </div>

      <div className="flex justify-center gap-4">
        <button
          onClick={onReset}
          className="bg-slate-800 hover:bg-slate-700 text-white px-6 py-3 rounded-xl font-medium transition"
        >
          Run Another Demo
        </button>
        <Link
          href="/dashboard"
          className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-medium transition inline-block"
        >
          Go to Dashboard →
        </Link>
      </div>
    </div>
  );
}

function DemoConsole({ logs, consoleEndRef }: { logs: ConsoleLog[]; consoleEndRef: any }) {
  const typeColors: Record<ConsoleLog["type"], string> = {
    info: "text-slate-400",
    action: "text-blue-400",
    success: "text-green-400",
    warning: "text-yellow-400",
    revenue: "text-emerald-400",
  };

  return (
    <div className="border-t border-slate-800 bg-slate-950">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center gap-2 py-2 text-xs text-slate-500 uppercase tracking-wide">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          System Console
        </div>
        <div className="h-48 overflow-y-auto font-mono text-sm space-y-1 pb-4">
          {logs.length === 0 && (
            <div className="text-slate-600 italic">Waiting for demo events...</div>
          )}
          {logs.map((log) => (
            <div key={log.id} className="flex items-start gap-2">
              <span className="text-slate-600 shrink-0">[{log.timestamp}]</span>
              <span className="text-slate-500 shrink-0">{log.agent}:</span>
              <span className={typeColors[log.type]}>{log.message}</span>
            </div>
          ))}
          <div ref={consoleEndRef} />
        </div>
      </div>
    </div>
  );
}
