const BASE_URL = process.env.NEXT_PUBLIC_API_URL;
let csrfToken: string | null = null;

function isUnsafeMethod(method: string) {
  return !["GET", "HEAD", "OPTIONS"].includes(method.toUpperCase());
}

async function request(endpoint: string, options: RequestInit = {}) {
  const method = options.method || "GET";
  const headers = new Headers(options.headers);

  if (csrfToken && isUnsafeMethod(method)) {
    headers.set("X-CSRF-Token", csrfToken);
  }

  const res = await fetch(`${BASE_URL}${endpoint}`, {
    credentials: "include", 
    ...options,
    method,
    headers,
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
  await request("/logout", { method: "POST" });
  csrfToken = null;
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
export const syncEmails = () => request("/sync", { method: "POST" });

// Process
export const processEmails = () => request("/process", { method: "POST" });

// Current user
export const getMe = async () => {
  const user = await request("/me");
  csrfToken = user.csrf_token;
  return user;
};


