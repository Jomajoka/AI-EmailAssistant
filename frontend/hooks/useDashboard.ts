import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getEmails, syncEmails, processEmails, getMe, getMeetings, getTasks } from "@/lib/api";
import type { Email, Meeting, Task } from "@/types";
import { updateTaskStatus } from "@/lib/api";
import toast from "react-hot-toast";

type User = {
  user_id: number;
  email: string;
  created_at: string;
  last_sync_time: string;
  csrf_token: string;
};


export function useDashboard() {
  const router = useRouter();

  //const [user, setUser] = useState<any>(null);
  const [user, setUser] = useState<User | null>(null)
  const [emails, setEmails] = useState<Email[]>([]);
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  

    const handleToggleTask = async (taskId: number, currentStatus: string) => {
    const newStatus = currentStatus === "completed" ? "pending" : "completed";

    setTasks((prev) =>
        prev.map((t) => t.id === taskId ? { ...t, status: newStatus } : t)
    );

    try {
        await updateTaskStatus(taskId, newStatus);
        toast.success(newStatus === "completed" ? "Task completed" : "Task reopened");
    } catch (err) {
        console.error(err);
        toast.error("Failed to update task");
        setTasks((prev) =>
        prev.map((t) => t.id === taskId ? { ...t, status: currentStatus } : t)
        );
    }
    };


  const fetchEmails = async () => {
    try { setEmails(await getEmails()); } catch (err) { console.error(err); }
  };

  const fetchMeetings = async () => {
    try { setMeetings(await getMeetings()); } catch (err) { console.error(err); }
  };

  const fetchTasks = async () => {
    try { setTasks(await getTasks()); } catch (err) { console.error(err); }
  };

    const handleSync = async () => {
    setLoading(true);
    try {
        await syncEmails();
        await fetchEmails();
        await fetchTasks();
        await fetchMeetings();
        toast.success("Emails synced successfully");
    } catch (err) {
        console.error(err);
        toast.error("Sync failed, please try again");
    } finally {
        setLoading(false);
    }
    };

    const handleProcess = async () => {
    setLoading(true);
    try {
        await processEmails();
        await fetchEmails();
        await fetchTasks();
        await fetchMeetings();
        toast.success("Emails processed successfully");
    } catch (err) {
        console.error(err);
        toast.error("Processing failed, please try again");
    } finally {
        setLoading(false);
    }
    };

  useEffect(() => {
    let active = true;

    getMe()
      .then((data) => {
        if (active) setUser(data);
      })
      .catch(() => {
        if (active) router.push("/login");
      })
      .finally(() => {
        if (active) setCheckingAuth(false);
      });

    getEmails()
      .then((data) => {
        if (active) setEmails(data);
      })
      .catch((err) => console.error(err));

    getMeetings()
      .then((data) => {
        if (active) setMeetings(data);
      })
      .catch((err) => console.error(err));

    getTasks()
      .then((data) => {
        if (active) setTasks(data);
      })
      .catch((err) => console.error(err));

    return () => {
      active = false;
    };
  }, [router]);

  return { user, emails, meetings, tasks, loading, checkingAuth, handleSync, handleProcess, handleToggleTask };
}
