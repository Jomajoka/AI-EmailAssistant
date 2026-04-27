"use client";

import { useState, useRef, useEffect } from "react";
import type { Task } from "@/types";
import TaskCard from "./TaskCard";

type Props = {
  tasks: Task[];
  onToggleTask: (taskId: number, currentStatus: string) => void;
};


type PriorityFilter = "All" | "High" | "Medium" | "Low";
type DueDateFilter = "All" | "Overdue" | "Today" | "This Week" | "Upcoming";

function getDueDateCategory(due_date?: string): DueDateFilter {
  if (!due_date) return "Upcoming";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(due_date);
  due.setHours(0, 0, 0, 0);
  const diffDays = Math.round((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return "Overdue";
  if (diffDays === 0) return "Today";
  if (diffDays <= 7) return "This Week";
  return "Upcoming";
}

function normalizePriority(priority?: string): string {
  if (!priority) return "Low";
  return priority.charAt(0).toUpperCase() + priority.slice(1).toLowerCase();
}

export default function TaskList({ tasks,onToggleTask }: Props) {
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>("All");
  const [dueDateFilter, setDueDateFilter] = useState<DueDateFilter>("All");
  const [showFilters, setShowFilters] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);
  const [hideCompleted, setHideCompleted] = useState(true);
  // Close filter overlay when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (filterRef.current && !filterRef.current.contains(e.target as Node)) {
        setShowFilters(false);
      }
    }
    if (showFilters) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showFilters]);

    const filtered = tasks.filter((task) => {
    const normalized = normalizePriority(task.priority);
    const priorityMatch = priorityFilter === "All" || normalized === priorityFilter;
    const dueDateMatch =
        dueDateFilter === "All" ||
        getDueDateCategory(task.due_date) === dueDateFilter;
    const completedMatch = !hideCompleted || task.status !== "completed";
    return priorityMatch && dueDateMatch && completedMatch;
    });

  const hasActiveFilter = priorityFilter !== "All" || dueDateFilter !== "All" || !hideCompleted;

  return (
    <div className="flex flex-col gap-2">

      {/* Header row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Tasks</h2>
          <span className="text-xs text-gray-400">
            {filtered.length} of {tasks.length}
          </span>
        </div>

        {/* Filter toggle with overlay */}
        <div className="relative" ref={filterRef}>
          <button
            onClick={() => setShowFilters((v) => !v)}
            className={`text-xs px-2.5 py-1 rounded-lg border transition-all ${
              hasActiveFilter
                ? "bg-gray-800 text-white border-gray-800"
                : showFilters
                ? "bg-gray-100 text-gray-700 border-gray-300"
                : "text-gray-500 border-gray-200 hover:border-gray-400"
            }`}
          >
            {hasActiveFilter ? "Filtered ✕" : "Filter"}
          </button>

          {/* Overlay dropdown */}
          {showFilters && (
            <div className="absolute right-0 top-8 z-10 w-56 bg-white border border-gray-200 rounded-xl shadow-lg p-3 flex flex-col gap-3">
              
              {/* Priority */}
              <div>
                <p className="text-xs text-gray-400 mb-1.5 font-medium">Priority</p>
                <div className="flex gap-1 flex-wrap">
                  {(["All", "High", "Medium", "Low"] as PriorityFilter[]).map((f) => (
                    <button
                      key={f}
                      onClick={() => setPriorityFilter(f)}
                      className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                        priorityFilter === f
                          ? "bg-gray-800 text-white border-gray-800"
                          : "text-gray-500 border-gray-200 hover:border-gray-400"
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              {/* Due date */}
              <div>
                <p className="text-xs text-gray-400 mb-1.5 font-medium">Due date</p>
                <div className="flex gap-1 flex-wrap">
                  {(["All", "Overdue", "Today", "This Week", "Upcoming"] as DueDateFilter[]).map((f) => (
                    <button
                      key={f}
                      onClick={() => setDueDateFilter(f)}
                      className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                        dueDateFilter === f
                          ? "bg-gray-800 text-white border-gray-800"
                          : "text-gray-500 border-gray-200 hover:border-gray-400"
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

                <div className="border-t border-gray-100 pt-2">
                <button
                    onClick={() => setHideCompleted((v) => !v)}
                    className={`text-xs px-2.5 py-1 rounded-full border transition-all ${
                    hideCompleted
                        ? "bg-gray-800 text-white border-gray-800"
                        : "text-gray-500 border-gray-200 hover:border-gray-400"
                    }`}
                >
                    {hideCompleted ? "Showing active only" : "Showing all tasks"}
                </button>
                </div>

              {/* Clear filters */}
              {hasActiveFilter && (
                <button
                  onClick={() => {
                    setPriorityFilter("All");
                    setDueDateFilter("All");
                  }}
                  className="text-xs text-red-400 hover:text-red-600 text-left transition-all"
                >
                  Clear filters
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Scrollable task list */}
      <div className="overflow-y-auto max-h-52 space-y-2 pr-1">
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-8">No tasks match.</p>
        ) : (
          filtered.map((task) => (
             <TaskCard key={task.id} task={task} onToggle={onToggleTask} />
          ))
        )}
      </div>

    </div>
  );
}