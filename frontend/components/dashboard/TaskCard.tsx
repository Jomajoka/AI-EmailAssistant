import type { Task } from "@/types";

type Props = {
  task: Task;
  onToggle: (taskId: number, currentStatus: string) => void;
};

const priorityColors: Record<string, string> = {
  High: "bg-red-100 text-red-700",
  Medium: "bg-yellow-100 text-yellow-700",
  Low: "bg-green-100 text-green-700",
};

function getDueDateStatus(due_date: string): { label: string; className: string } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(due_date);
  due.setHours(0, 0, 0, 0);

  const diffDays = Math.round((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) return { label: `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? "s" : ""}`, className: "text-red-500" };
  if (diffDays === 0) return { label: "Due today", className: "text-orange-500" };
  if (diffDays === 1) return { label: "Due tomorrow", className: "text-yellow-600" };
  if (diffDays <= 7) return { label: `${diffDays} days left`, className: "text-yellow-600" };
  return { label: `${diffDays} days left`, className: "text-gray-400" };
}




export default function TaskCard({ task, onToggle }: Props) {
  const priority = task.priority || "Low";
  const isCompleted = task.status === "completed";

  return (
    <div className={`flex gap-3 p-3 rounded-lg border transition-all ${
      isCompleted
        ? "border-gray-100 bg-gray-50 opacity-60"
        : "border-gray-100 hover:border-gray-200 hover:bg-gray-50"
    }`}>

      {/* Checkbox — now wired up */}
      <button
        onClick={() => onToggle(task.id, task.status || "pending")}
        className={`w-5 h-5 shrink-0 mt-0.5 rounded-full border-2 transition-all ${
          isCompleted
            ? "border-green-500 bg-green-500"
            : "border-gray-300 hover:border-gray-400"
        }`}
      >
        {isCompleted && (
          <svg viewBox="0 0 10 10" className="w-full h-full p-0.5" fill="none">
            <path
              d="M2 5l2.5 2.5L8 3"
              stroke="white"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className={`text-sm font-medium truncate ${
            isCompleted ? "line-through text-gray-400" : "text-gray-800"
          }`}>
            {task.title}
          </p>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${priorityColors[priority] ?? priorityColors["Low"]}`}>
            {priority}
          </span>
        </div>

        {task.description && (
          <p className="text-xs text-gray-400 mt-0.5 truncate">{task.description}</p>
        )}

        {task.due_date && (
          <div className="flex items-center gap-2 mt-1">
            <p className="text-xs text-gray-400">
              Due {new Date(task.due_date).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              })}
            </p>
            {!isCompleted && (
              <>
                <span className="text-xs text-gray-300">·</span>
                {(() => {
                  const { label, className } = getDueDateStatus(task.due_date);
                  return <p className={`text-xs font-medium ${className}`}>{label}</p>;
                })()}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}