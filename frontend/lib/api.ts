const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function request(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    credentials: "include", 
    ...options,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "API request failed");
  }

  return res.json();
}

//login
export const login = () => {
  window.location.href = `${BASE_URL}/login`;
};

//logout
export const logout = async () => {
  await request("/logout");
  window.location.href = "/login";
};

export const updateTaskStatus = (taskId: number, status: string) =>
  request(`/tasks/${taskId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });


// Emails
export const getEmails = () => request("/emails");

// Tasks
export const getTasks = () => request("/tasks");

// Meetings
export const getMeetings = () => request("/meetings");

// Sync
export const syncEmails = () => request("/sync");

// Process
export const processEmails = () => request("/process");

// Current user
export const getMe = () => request("/me");


