"use client";

import { useState } from "react";
import { useDashboard } from "@/hooks/useDashboard";
import EmailList from "@/components/dashboard/EmailList";
import MeetingList from "@/components/dashboard/MeetingList";
import TaskList from "@/components/dashboard/TaskList";
import ActionBar from "@/components/dashboard/ActionBar";
import MeetingCalendar from "@/components/dashboard/MeetingCalendar";
import ProfileButton from "@/components/dashboard/ProfileButton";


type MeetingView = "list" | "calendar";

export default function Dashboard() {
  const { user, emails, meetings, tasks, loading, checkingAuth, handleSync, handleProcess, handleToggleTask } = useDashboard();
  const [meetingView, setMeetingView] = useState<MeetingView>("list");

  if (checkingAuth) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-400 text-sm">
        Checking authentication...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">

    {/* Header */}
    <div className="flex items-center justify-between mb-6">
      <h1 className="text-xl font-semibold text-gray-800">Intelligence Dashboard</h1>
      <div className="flex items-center gap-3">
        <ActionBar loading={loading} onSync={handleSync} onProcess={handleProcess} />
        <ProfileButton user={user} />
      </div>
    </div>

      {/* Main grid */}
      <div className="grid grid-cols-3 gap-6">

      {/* Left — Emails (2/3 width) */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 col-span-2 flex flex-col">
        <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
          Emails
        </h2>
        <div className="overflow-y-auto max-h-[600px] pr-1">
          <EmailList emails={emails} />
        </div>
      </div>

      {/* Right column */}
      <div className="col-span-1 flex flex-col gap-6">

      {/* Meetings */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
            Meetings
          </h2>
          <div className="flex gap-1 bg-gray-100 rounded-lg p-1 text-xs">
            <button
              onClick={() => setMeetingView("list")}
              className={`px-3 py-1 rounded-md transition-all ${
                meetingView === "list"
                  ? "bg-white text-gray-800 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              List
            </button>
            <button
              onClick={() => setMeetingView("calendar")}
              className={`px-3 py-1 rounded-md transition-all ${
                meetingView === "calendar"
                  ? "bg-white text-gray-800 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              Calendar
            </button>
          </div>
        </div>

        {/* No scroll wrapper in calendar mode */}
        {meetingView === "list" ? (
          <div className="overflow-y-auto max-h-64 pr-1">
            <MeetingList meetings={meetings} />
          </div>
        ) : (
          <MeetingCalendar meetings={meetings} />
        )}
      </div>

        {/* Tasks */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <TaskList tasks={tasks} onToggleTask={handleToggleTask} />
        </div>

      </div>
      </div>
    </div>
  );
}