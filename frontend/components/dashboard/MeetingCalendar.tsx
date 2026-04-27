import { useState } from "react";
import type { Meeting } from "@/types";

type Props = {
  meetings: Meeting[];
};

function formatTime(time?: string) {
  if (!time) return "";
  const [h, m] = time.split(":");
  const hour = parseInt(h);
  const ampm = hour >= 12 ? "PM" : "AM";
  return `${hour % 12 || 12}:${m} ${ampm}`;
}

function getDaysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year: number, month: number) {
  return new Date(year, month, 1).getDay();
}

const DAYS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function MeetingCalendar({ meetings }: Props) {
  const today = new Date();
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [selectedDay, setSelectedDay] = useState<number | null>(null);

  const daysInMonth = getDaysInMonth(currentYear, currentMonth);
  const firstDay = getFirstDayOfMonth(currentYear, currentMonth);

  // Group meetings by day for current month/year
  const meetingsByDay: Record<number, Meeting[]> = {};
  meetings.forEach((meeting) => {
    const date = new Date(meeting.meeting_date);
    if (
      date.getMonth() === currentMonth &&
      date.getFullYear() === currentYear
    ) {
      const day = date.getDate();
      if (!meetingsByDay[day]) meetingsByDay[day] = [];
      meetingsByDay[day].push(meeting);
    }
  });

  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear((y) => y - 1);
    } else {
      setCurrentMonth((m) => m - 1);
    }
    setSelectedDay(null);
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear((y) => y + 1);
    } else {
      setCurrentMonth((m) => m + 1);
    }
    setSelectedDay(null);
  };

  const handleDayClick = (day: number) => {
    if (meetingsByDay[day]) setSelectedDay(day);
  };

  // --- Day detail view ---
  if (selectedDay !== null) {
    const dayMeetings = meetingsByDay[selectedDay] || [];
    return (
      <div>
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={() => setSelectedDay(null)}
            className="text-xs text-gray-500 hover:text-gray-800 flex items-center gap-1 transition-all"
          >
            ← Back
          </button>
          <p className="text-sm font-semibold text-gray-700">
            {new Date(currentYear, currentMonth, selectedDay).toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>

        {/* Meeting details */}
        <div className="space-y-3">
          {dayMeetings.map((meeting, index) => (
            <div
              key={index}
              className="p-3 rounded-lg border border-blue-100 bg-blue-50"
            >
              <p className="text-sm font-medium text-gray-800">{meeting.title}</p>
              {(meeting.start_time || meeting.end_time) && (
                <p className="text-xs text-blue-500 mt-0.5">
                  {formatTime(meeting.start_time)}
                  {meeting.end_time ? ` → ${formatTime(meeting.end_time)}` : ""}
                </p>
              )}
              {meeting.description && (
                <p className="text-xs text-gray-500 mt-1">{meeting.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  // --- Calendar view ---
  return (
    <div>
      {/* Month navigation */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={handlePrevMonth}
          className="text-gray-400 hover:text-gray-700 text-sm px-1 transition-all"
        >
          ‹
        </button>
        <p className="text-sm font-semibold text-gray-700">
          {MONTHS[currentMonth]} {currentYear}
        </p>
        <button
          onClick={handleNextMonth}
          className="text-gray-400 hover:text-gray-700 text-sm px-1 transition-all"
        >
          ›
        </button>
      </div>

        {/* Day headers */}
        <div className="grid grid-cols-7 border-t border-l border-gray-400 mb-0">
        {DAYS.map((d) => (
            <p key={d} className="text-center text-xs text-gray-800 font-medium py-1 border-r border-b border-gray-400">
            {d}
            </p>
        ))}
        </div>

        {/* Day cells */}
        <div className="grid grid-cols-7 border-l border-gray-400">
        {Array.from({ length: firstDay }).map((_, i) => (
            <div key={`empty-${i}`} className="border-r border-b border-gray-400 h-12" />
        ))}

        {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const dayMeetings = meetingsByDay[day];
            const isToday =
            day === today.getDate() &&
            currentMonth === today.getMonth() &&
            currentYear === today.getFullYear();
            const hasMeetings = !!dayMeetings;

            return (
            <div
                key={day}
                onClick={() => handleDayClick(day)}
                className={`flex flex-col items-center py-1 h-12 border-r border-b border-gray-400 transition-all ${
                hasMeetings ? "cursor-pointer hover:bg-blue-50" : ""
                }`}
            >
                <span
                className={`text-xs w-6 h-6 flex items-center justify-center rounded-full font-medium ${
                    isToday
                    ? "bg-gray-800 text-white"
                    : hasMeetings
                    ? "text-gray-800"
                    : "text-gray-800"
                }`}
                >
                {day}
                </span>

                {hasMeetings && (
                <span className="mt-0.5 text-xs bg-blue-100 text-blue-600 font-medium px-1.5 py-0.5 rounded-full leading-none">
                    {dayMeetings.length === 1 ? "1" : `+${dayMeetings.length}`}
                </span>
                )}
            </div>
            );
        })}
        </div>
    </div>
  );
}