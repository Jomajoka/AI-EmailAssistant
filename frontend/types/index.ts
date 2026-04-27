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
export type { Email, Meeting, Task };