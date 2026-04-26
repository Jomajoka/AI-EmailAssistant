"use client";

import { useEffect, useState } from "react";
import {
  getEmails,
  syncEmails,
  processEmails,
  getMe,
  getMeetings,
  getTasks
} from "@/lib/api";
import { useRouter } from "next/navigation";

type Email = {
  sender: string;
  subject: string;
  received_at: string;
  summary?: string;
  category?: string;
  priority?: string;
};

type Meeting = {
  title: string;
  meeting_date: string;
  start_time?: string;
  end_time?: string;
  description?: string;
};

type Task = {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority?: string;
  status?: string;
};



export default function Dashboard() {
  const router = useRouter();

  const [emails, setEmails] = useState<Email[]>([]);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);

  // 🔐 Check user
  const fetchUser = async () => {
    try {
      const data = await getMe();
      setUser(data);
    } catch {
      router.push("/login");
    } finally {
      setCheckingAuth(false);
    }
  };

  // 📩 Fetch emails
  const fetchEmails = async () => {
    try {
      const data = await getEmails();
      setEmails(data);
    } catch (err) {
      console.error("Error fetching emails:", err);
    }
  };

  const fetchTasks = async () => {
  try {
    const data = await getTasks();
    setTasks(data);
  } catch (err) {
    console.error("Error fetching tasks:", err);
  }
  };

  // 🔄 Sync emails
  const handleSync = async () => {
    setLoading(true);
    try {
      await syncEmails();
      await fetchEmails();
    } catch (err) {
      console.error("Sync failed:", err);
    } finally {
      setLoading(false);
    }
  };

  // 🤖 Process emails
  const handleProcess = async () => {
    setLoading(true);
    try {
      await processEmails();
      await fetchEmails();
    } catch (err) {
      console.error("Process failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMeetings = async () => {
    try {
      const data = await getMeetings();
      setMeetings(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchUser();
    fetchEmails();
    fetchMeetings();
    fetchTasks();
  }, []);

  // ⏳ Prevent flicker before auth check
  if (checkingAuth) {
    return <p className="p-6">Checking authentication...</p>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Email Dashboard</h1>

      {/* Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleSync}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          {loading ? "Syncing..." : "Sync Emails"}
        </button>

        <button
          onClick={handleProcess}
          className="bg-green-500 text-white px-4 py-2 rounded"
        >
          {loading ? "Processing..." : "Process Emails"}
        </button>
      </div>

      {/* Email List */}
      <div className="space-y-4">
        {emails.length === 0 ? (
          <p>No emails found.</p>
        ) : (
          emails.map((email, index) => (
            <div
              key={index}
              className="border p-4 rounded shadow-sm bg-white"
            >
              <p className="text-sm text-gray-500">{email.sender}</p>
              <h2 className="font-semibold">{email.subject}</h2>
              <p className="text-sm">
                {email.summary || "No summary yet"}
              </p>

              <div className="flex gap-2 mt-2 text-xs">
                <span className="bg-gray-200 px-2 py-1 rounded">
                  {email.category || "Unknown"}
                </span>
                <span className="bg-gray-200 px-2 py-1 rounded">
                  {email.priority || "Low"}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* Meetings */}
      <h2 className="text-xl font-semibold mt-8 mb-4">Meetings</h2>
      <div className="space-y-3">
        {meetings.length === 0 ? (
          <p>No meetings found.</p>
        ) : (
          meetings.map((meeting, index) => (
            <div key={index} className="border p-3 rounded bg-white">
              <h3 className="font-medium">{meeting.title}</h3>
              <p className="text-sm text-gray-600">
                {meeting.meeting_date} {meeting.start_time || ""}
              </p>
            </div>
          ))
        )}
      </div>

      {/* Tasks */}
      <h2 className="text-xl font-semibold mt-8 mb-4">Tasks</h2>

      <div className="space-y-3">
        {tasks.length === 0 ? (
          <p>No tasks found.</p>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="border p-3 rounded bg-white">
              <h3 className="font-medium">{task.title}</h3>

              {task.description && (
                <p className="text-sm text-gray-600">{task.description}</p>
              )}

              <div className="flex gap-2 mt-2 text-xs">
                {task.due_date && (
                  <span className="bg-gray-200 px-2 py-1 rounded">
                    Due: {task.due_date}
                  </span>
                )}
                <span className="bg-gray-200 px-2 py-1 rounded">
                  {task.priority || "Low"}
                </span>
                <span className="bg-gray-200 px-2 py-1 rounded">
                  {task.status || "pending"}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}