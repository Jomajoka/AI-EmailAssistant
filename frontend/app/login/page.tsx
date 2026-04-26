"use client";

import { login } from "@/lib/api";

export default function LoginPage() {
  return (
    <div className="h-screen flex items-center justify-center">
      <div className="p-6 border rounded shadow-md text-center">
        <h1 className="text-xl font-bold mb-4">Email Assistant</h1>

        <button
          onClick={login}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Login with Google
        </button>
      </div>
    </div>
  );
}