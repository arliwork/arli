"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { MessageSquare, Clock, CheckCircle, XCircle, Loader2, Send, User, Bot, ArrowLeft } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface TaskDetail {
  task_id: string;
  description: string;
  status: string;
  assigned_role: string;
  success?: boolean;
  result_data?: any;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

interface Comment {
  id: string;
  author_type: string;
  author_name: string;
  content: string;
  created_at: string;
}

export default function TaskDetailPage() {
  const params = useParams();
  const taskId = params.taskId as string;

  const [task, setTask] = useState<TaskDetail | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (taskId) {
      fetchTask();
      fetchComments();
    }
  }, [taskId]);

  const fetchTask = async () => {
    try {
      const res = await fetch(`${API_URL}/tasks/${taskId}`);
      if (res.ok) {
        const data = await res.json();
        setTask(data);
      }
    } catch (e) {}
    setLoading(false);
  };

  const fetchComments = async () => {
    try {
      const res = await fetch(`${API_URL}/tasks/${taskId}/comments`);
      if (res.ok) {
        const data = await res.json();
        setComments(data.items || []);
      }
    } catch (e) {}
  };

  const submitComment = async () => {
    if (!newComment.trim()) return;
    try {
      const res = await fetch(`${API_URL}/tasks/${taskId}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_id: taskId,
          author_type: "user",
          author_id: "user-1",
          author_name: "You",
          content: newComment,
        }),
      });
      if (res.ok) {
        setNewComment("");
        fetchComments();
      }
    } catch (e) {
      toast.error("Failed to send comment");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed": return <XCircle className="w-5 h-5 text-red-500" />;
      case "in_progress": return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default: return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>;
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Task not found</p>
          <Link href="/dashboard" className="text-blue-600 text-sm mt-2 inline-block">Back to Dashboard</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavHeader />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <Link href="/dashboard" className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>

        <div className="bg-white rounded-xl shadow border p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            {getStatusIcon(task.status)}
            <div>
              <h1 className="text-xl font-bold">{task.description}</h1>
              <p className="text-sm text-gray-500">{task.task_id} · {task.assigned_role}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
            <div>
              <p className="text-gray-500">Status</p>
              <p className="font-medium capitalize">{task.status}</p>
            </div>
            <div>
              <p className="text-gray-500">Created</p>
              <p className="font-medium">{new Date(task.created_at).toLocaleDateString()}</p>
            </div>
            {task.started_at && (
              <div>
                <p className="text-gray-500">Started</p>
                <p className="font-medium">{new Date(task.started_at).toLocaleDateString()}</p>
              </div>
            )}
            {task.completed_at && (
              <div>
                <p className="text-gray-500">Completed</p>
                <p className="font-medium">{new Date(task.completed_at).toLocaleDateString()}</p>
              </div>
            )}
          </div>

          {task.result_data?.output && (
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Result</p>
              <pre className="text-sm text-gray-600 whitespace-pre-wrap font-mono max-h-96 overflow-y-auto">{task.result_data.output}</pre>
            </div>
          )}

          {task.error_message && (
            <div className="bg-red-50 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-red-700 mb-1">Error</p>
              <p className="text-sm text-red-600">{task.error_message}</p>
            </div>
          )}
        </div>

        {/* Comments */}
        <div className="bg-white rounded-xl shadow border p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-600" />
            Discussion
          </h2>

          <div className="space-y-4 mb-6 max-h-[500px] overflow-y-auto">
            {comments.length === 0 ? (
              <p className="text-gray-500 text-center py-4">No comments yet</p>
            ) : (
              comments.map((c) => (
                <div key={c.id} className="flex gap-3">
                  <div className="mt-0.5">
                    {c.author_type === "agent" ? (
                      <Bot className="w-5 h-5 text-purple-600" />
                    ) : (
                      <User className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium">{c.author_name || c.author_type}</span>
                      <span className="text-xs text-gray-400">{new Date(c.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{c.content}</p>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="flex gap-2 pt-4 border-t">
            <input
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submitComment()}
              placeholder="Add a comment..."
              className="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={submitComment}
              disabled={!newComment.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-1"
            >
              <Send className="w-4 h-4" />
            </button>
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
          <Link href="/approvals" className="text-gray-600 hover:text-gray-900 text-sm">Approvals</Link>
          <Link href="/activity" className="text-gray-600 hover:text-gray-900 text-sm">Activity</Link>
        </div>
      </div>
    </header>
  );
}
