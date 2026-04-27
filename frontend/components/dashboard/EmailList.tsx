import type { Email } from "@/types";
import EmailCard from "./EmailCard";

type Props = {
  emails: Email[];
};

export default function EmailList({ emails }: Props) {
  if (emails.length === 0) {
    return <p className="text-sm text-gray-400 text-center py-8">No emails found.</p>;
  }

  return (
    <div className="divide-y divide-gray-100">
      {emails.map((email, index) => (
        <EmailCard key={index} email={email} />
      ))}
    </div>
  );
}