"use client";
import type { Incident } from "@/app/lib/services/api";
type IncidentHeaderProps = {
  incident: Incident;
  isInvestigating: boolean;
  isUpdatingStatus: boolean;
  onInvestigate: () => void;
  onStatusChange: (status: Incident["status"]) => void;
};
const severityStyles: Record<Incident["severity"], string> = {
  low: "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400 border-green-200 dark:border-green-500/20",
  medium:
    "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400 border-yellow-200 dark:border-yellow-500/20",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400 border-orange-200 dark:border-orange-500/20",
  critical:
    "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 border-red-200 dark:border-red-500/20",
};

const statusStyles: Record<Incident["status"], string> = {
  open: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20",
  investigating:
    "bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/20",
  contained:
    "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-500/10 dark:text-yellow-400 dark:border-yellow-500/20",
  resolved:
    "bg-green-100 text-green-700 border-green-200 dark:bg-green-500/10 dark:text-green-400 dark:border-green-500/20",
  closed:
    "bg-black/5 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-800 dark:bg-white/5",
};
export default function IncidentHeader({
  incident,
  isInvestigating,
  isUpdatingStatus,
  onInvestigate,
  onStatusChange,
}: IncidentHeaderProps) {
  return (
    <header className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
            Incident #{incident.id}
          </p>
          <h1 className="mt-1 text-2xl font-bold text-gray-900 dark:text-gray-100">
            {incident.title}
          </h1>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span
            className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
              severityStyles[incident.severity]
            }`}
          >
            {incident.severity}
          </span>

          <span
            className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
              statusStyles[incident.status]
            }`}
          >
            {incident.status}
          </span>

          <select
            value={incident.status}
            onChange={(event) =>
              onStatusChange(event.target.value as Incident["status"])
            }
            disabled={isUpdatingStatus}
            aria-label="Update incident status"
            className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-3 py-1.5 text-sm font-medium text-gray-900 dark:text-gray-100 outline-none transition focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="contained">Contained</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>

          <button
            type="button"
            onClick={onInvestigate}
            disabled={isInvestigating}
            className="rounded-full bg-blue-600 dark:bg-blue-500 px-4 py-1.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isInvestigating ? "Investigating..." : "Investigate"}
          </button>
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          Description
        </h2>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-gray-500 dark:text-gray-400">
          {incident.description}
        </p>
      </div>
    </header>
  );
}
