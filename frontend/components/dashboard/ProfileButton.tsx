"use client";

import { useState, useRef, useEffect } from "react";
import { logout } from "@/lib/api";

type User = {
  user_id: number;
  email: string;
  created_at: string;
  last_sync_time: string;
};

type Props = {
  user: User | null;
};

function getInitials(email: string) {
  const name = email.split("@")[0];
  return name
    .split(/[._-]/)
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

function formatName(email: string) {
  const name = email.split("@")[0];
  return name
    .split(/[._-]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function ProfileButton({ user }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  if (!user) return null;

  return (
    <div className="relative" ref={ref}>
      
      {/* Avatar button */}
        <button
        onClick={() => setOpen((v) => !v)}
        title={formatName(user.email)}
        className="w-8 h-8 rounded-full bg-gray-800 text-white text-xs font-medium flex items-center justify-center hover:bg-gray-700 transition-all"
        >
        {getInitials(user.email)}
        </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 top-10 z-20 w-64 bg-white border border-gray-200 rounded-xl shadow-lg p-4 flex flex-col gap-3">
          
        {/* User info */}
        <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gray-800 text-white text-sm font-medium flex items-center justify-center shrink-0">
            {getInitials(user.email)}
        </div>
        <div className="min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">
            {formatName(user.email)}
            </p>
            <p className="text-xs text-gray-400 truncate">{user.email}</p>
        </div>
        </div>

          <div className="border-t border-gray-100" />

          {/* Meta info */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between">
              <p className="text-xs text-gray-400">Member since</p>
              <p className="text-xs text-gray-600">{formatDate(user.created_at)}</p>
            </div>
            <div className="flex justify-between">
              <p className="text-xs text-gray-400">Last sync</p>
              <p className="text-xs text-gray-600">
                {user.last_sync_time ? formatDate(user.last_sync_time) : "Never"}
              </p>
            </div>
          </div>

          <div className="border-t border-gray-100" />

          {/* Logout */}
          <button
            onClick={logout}
            className="w-full text-xs text-red-500 hover:text-red-700 hover:bg-red-50 py-1.5 rounded-lg transition-all text-left px-2"
          >
            Sign out
          </button>

        </div>
      )}
    </div>
  );
} 