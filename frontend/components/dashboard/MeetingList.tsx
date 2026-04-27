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

export default function MeetingList({ meetings }: Props) {
  if (meetings.length === 0) {
    return <p className="text-sm text-gray-400 text-center py-8">No meetings found.</p>;
  }

  return (
    <div className="space-y-2">
      {meetings.map((meeting, index) => (
        <div
          key={index}
          className="flex gap-3 p-3 rounded-lg border border-gray-100 hover:border-gray-200 hover:bg-gray-50 transition-all"
        >
          {/* Date block */}
          <div className="w-10 shrink-0 flex flex-col items-center justify-center bg-blue-50 rounded-lg py-1.5">
            <p className="text-xs text-blue-400 font-medium uppercase leading-none">
              {new Date(meeting.meeting_date).toLocaleDateString("en-US", { month: "short" })}
            </p>
            <p className="text-lg font-semibold text-blue-700 leading-tight">
              {new Date(meeting.meeting_date).getDate()}
            </p>
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">{meeting.title}</p>
            <p className="text-xs text-gray-400 mt-0.5">
              {formatTime(meeting.start_time)}
              {meeting.end_time ? ` → ${formatTime(meeting.end_time)}` : ""}
            </p>
            {meeting.description && (
              <p className="text-xs text-gray-400 mt-0.5 truncate">{meeting.description}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}