"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Clock, Plus, Trash2, Loader2, Play, Pause, Calendar } from "lucide-react";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Schedule {
  schedule_id: string;
  name: string;
  schedule: string;
  pipeline_type: string;
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  run_count: number;
}

const SCHEDULE_OPTIONS = [
  { value: "hourly", label: "Every Hour" },
  { value: "daily", label: "Every Day" },
  { value: "weekly", label: "Every Week" },
];

const PIPELINE_OPTIONS = [
  { value: "plan-feature", label: "Plan Feature" },
  { value: "fix-bug", label: "Fix Bug" },
  { value: "refactor", label: "Refactor" },
];

export default function SchedulerPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    name: "",
    description: "",
    schedule: "daily",
    pipeline_type: "plan-feature",
  });

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      const res = await fetch(`${API_URL}/scheduler/schedules`);
      const data = await res.json();
      setSchedules(data.schedules || []);
    } catch (e) {
      toast.error("Failed to load schedules");
    } finally {
      setLoading(false);
    }
  };

  const createSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch(`${API_URL}/scheduler/schedules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (data.success) {
        toast.success("Schedule created");
        setShowForm(false);
        setForm({ name: "", description: "", schedule: "daily", pipeline_type: "plan-feature" });
        fetchSchedules();
      } else {
        toast.error(data.error || "Failed to create");
      }
    } catch (e) {
      toast.error("Network error");
    } finally {
      setSubmitting(false);
    }
  };

  const toggleSchedule = async (sched: Schedule) => {
    try {
      const res = await fetch(`${API_URL}/scheduler/schedules/${sched.schedule_id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !sched.is_active }),
      });
      const data = await res.json();
      if (data.success) {
        toast.success(sched.is_active ? "Paused" : "Activated");
        fetchSchedules();
      }
    } catch (e) {
      toast.error("Network error");
    }
  };

  const deleteSchedule = async (schedule_id: string) => {
    if (!confirm("Delete this schedule?")) return;
    try {
      const res = await fetch(`${API_URL}/scheduler/schedules/${schedule_id}`, {
        method: "DELETE",
      });
      const data = await res.json();
      if (data.success) {
        toast.success("Deleted");
        fetchSchedules();
      }
    } catch (e) {
      toast.error("Network error");
    }
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

      <main className="max-w-5xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Clock className="w-8 h-8 text-blue-600" />
              Scheduler
            </h1>
            <p className="text-gray-600 mt-1">Automate your AI companies with recurring workflows.</p>
          </div>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Schedule
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
            <h3 className="font-semibold text-gray-900 mb-4">Create Scheduled Workflow</h3>
            <form onSubmit={createSchedule} className="grid md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
          required
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Daily Market Report"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <input
                  type="text"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="What should this workflow do?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
                <select
                  value={form.schedule}
                  onChange={(e) => setForm({ ...form, schedule: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {SCHEDULE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pipeline</label>
                <select
                  value={form.pipeline_type}
                  onChange={(e) => setForm({ ...form, pipeline_type: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {PIPELINE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div className="md:col-span-2 flex gap-3">
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Schedule"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-blue-600" />
          </div>
        ) : schedules.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No schedules yet</h3>
            <p className="text-gray-600">Create your first recurring workflow to keep agents working 24/7.</p>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Name</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Frequency</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Pipeline</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Status</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Runs</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {schedules.map((s) => (
                  <tr key={s.schedule_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{s.name}</div>
                      <div className="text-xs text-gray-500">{s.schedule_id}</div>
                    </td>
                    <td className="px-4 py-3 capitalize text-gray-700">{s.schedule}</td>
                    <td className="px-4 py-3 text-gray-700">{s.pipeline_type}</td>
                    <td className="px-4 py-3">
                      <span className={`text-xs px-2 py-1 rounded-full ${s.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-700"}`}>
                        {s.is_active ? "Active" : "Paused"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{s.run_count}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => toggleSchedule(s)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition"
                          title={s.is_active ? "Pause" : "Activate"}
                        >
                          {s.is_active ? <Pause className="w-4 h-4 text-gray-600" /> : <Play className="w-4 h-4 text-green-600" />}
                        </button>
                        <button
                          onClick={() => deleteSchedule(s.schedule_id)}
                          className="p-2 hover:bg-red-50 rounded-lg transition"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
