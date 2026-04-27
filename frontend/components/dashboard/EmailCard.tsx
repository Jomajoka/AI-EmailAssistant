import type { Email } from "@/types";

type Props = {
  email: Email;
};

const priorityColors: Record<string, string> = {
  High: "bg-red-100 text-red-700",
  Medium: "bg-yellow-100 text-yellow-700",
  Low: "bg-green-100 text-green-700",
};

const categoryColors: Record<string, string> = {
  Work: "bg-blue-100 text-blue-700",
  Personal: "bg-purple-100 text-purple-700",
  Finance: "bg-orange-100 text-orange-700",
  Unknown: "bg-gray-100 text-gray-600",
};

function parseSender(sender: string): { name: string; email: string } {
  const match = sender.match(/^(.+?)\s*<(.+?)>$/);
  if (match) {
    return { name: match[1].trim(), email: match[2].trim() };
  }
  return { name: sender, email: "" };
}

function getInitials(name: string) {
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}


export default function EmailCard({ email }: Props) {
  const priority = email.priority || "Low";
  const category = email.category || "Unknown";
  const { name, email: senderEmail } = parseSender(email.sender);

  return (
    <div className="flex gap-3 p-3 rounded-lg hover:bg-gray-50 transition-all border border-transparent hover:border-gray-200">
      
      {/* Sender avatar */}
      <div className="w-9 h-9 rounded-full bg-gray-800 text-white flex items-center justify-center text-xs font-medium shrink-0">
        {getInitials(name)}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-0.5">
          <div className="flex items-center gap-1.5 min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">{name}</p>
            {senderEmail && (
              <p className="text-xs text-gray-400 truncate hidden sm:block">{senderEmail}</p>
            )}
          </div>
          <p className="text-xs text-gray-400 shrink-0">
            {new Date(email.received_at).toLocaleDateString()}
          </p>
        </div>

        <p className="text-sm text-gray-700 font-medium truncate">{email.subject}</p>
        <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">
          {email.summary || "No summary yet"}
        </p>

        <div className="flex gap-1.5 mt-2">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${categoryColors[category] ?? categoryColors["Unknown"]}`}>
            {category}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${priorityColors[priority] ?? priorityColors["Low"]}`}>
            {priority}
          </span>
        </div>
      </div>

    </div>
  );
}