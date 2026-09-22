"use client";
import {
  type Incident,
  useAssignIncidentMutation,
  useGetInvestigatorsQuery,
} from "@/app/lib/services/api";

import { useState } from "react";
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
  const { data: investigators = [], isLoading: isLoadingInvestigators } =
    useGetInvestigatorsQuery();

  const [assignIncident, { isLoading: isAssigning }] =
    useAssignIncidentMutation();
  const [assignmentError, setAssignmentError] = useState("");
  const [statusError, setStatusError] = useState("");
  const handleAssign = async (investigatorId: number) => {
    setAssignmentError("");
    try {
      await assignIncident({
        incidentId: incident.id,
        investigator_id: investigatorId,
      }).unwrap();
    } catch (error: unknown) {
      const apiError = error as {
        data?: {
          detail?: string;
        };
      };

      setAssignmentError(
        apiError?.data?.detail ?? "unable to assign this incident",
      );
    }
  };

  return (
    <header className="rounded-2xl glass-panel p-6 shadow-sm animate-fade-in-up">
      {assignmentError && (
        <p className="basis-full text-xs text-red-500">{assignmentError}</p>
      )}
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
          {/* Severity */}
          <span
            className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
              severityStyles[incident.severity]
            }`}
          >
            {incident.severity}
          </span>

          {/* Current status */}
          <span
            className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
              statusStyles[incident.status]
            }`}
          >
            {incident.status}
          </span>

          {/* Status selector */}
          <select
            value={incident.status}
            onChange={(event) => {
              onStatusChange(event.target.value as Incident["status"]);
            }}
            disabled={isUpdatingStatus}
            aria-label="Update incident status"
            className="rounded-lg border border-transparent bg-black/5 px-3 py-1.5 text-sm font-medium text-black outline-none transition focus:border-gray-300 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white/5 dark:text-white dark:focus:border-gray-700"
          >
            <option value={incident.status}>
              {incident.status.charAt(0).toUpperCase() +
                incident.status.slice(1)}
            </option>

            {incident.available_transitions?.map((status) => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>

          {/* Investigator selector */}
          <select
            value={incident.assigned_to ?? ""}
            onChange={(event) => {
              const value = event.target.value;

              if (!value) {
                return;
              }

              void handleAssign(Number(value));
            }}
            disabled={isLoadingInvestigators || isAssigning}
            aria-label="Assign investigator"
            className="rounded-lg border border-transparent bg-black/5 px-3 py-1.5 text-sm font-medium text-black outline-none transition focus:border-gray-300 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white/5 dark:text-white dark:focus:border-gray-700"
          >
            <option value="">
              {isLoadingInvestigators
                ? "Loading investigators..."
                : incident.assigned_to
                  ? "Change investigator"
                  : "Assign investigator"}
            </option>

            {investigators.map((investigator) => (
              <option key={investigator.id} value={investigator.id}>
                {investigator.name}
              </option>
            ))}
          </select>

          {/* Investigate */}
          <button
            type="button"
            onClick={onInvestigate}
            disabled={isInvestigating}
            className="rounded-full bg-black px-4 py-1.5 text-sm font-semibold text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
          >
            {isInvestigating ? "Investigating..." : "Investigate"}
          </button>
        </div>
      </div>

      {/* Description */}
      <div className="mt-6">
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          Description
        </h2>

        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-gray-500 dark:text-gray-400">
          {incident.description}
        </p>
      </div>

      {/* Associated Resources */}
      {incident.resources && incident.resources.length > 0 && (
        <div className="mt-6 border-t border-gray-200/50 dark:border-gray-800/50 pt-6">
          <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Associated Resources
          </h2>
          <div className="mt-3 flex flex-wrap gap-3">
            {incident.resources.map((res) => (
              <div
                key={res.id}
                className="inline-flex flex-col rounded-lg border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-3 py-2 text-xs"
              >
                <span className="font-semibold text-gray-700 dark:text-gray-300">
                  {res.provider} • {res.resource_type}
                </span>
                <span className="text-gray-500 dark:text-gray-400 mt-1">
                  {res.identifier}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
