"use client";
import { useGetIncidentAuditQuery } from "@/app/lib/services/api";

type AuditTimelineProps = {
  incidentId: number;
};

function formatAction(action: string) {
  return action
    .toLowerCase()
    .replace(/_/g, "")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export default function AuditTimeline({ incidentId }: AuditTimelineProps) {
  const {
    data: auditLogs = [],
    isLoading,
    isError,
  } = useGetIncidentAuditQuery(incidentId);

  return (
    <section className="rounded-2xl glass-panel p-6 shadow-sm">
      <header className="mb-6">
        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          Activity
        </h2>

        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          History of changes and actions performed on this incident.
        </p>
      </header>

      {isLoading && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Loading activity...
        </p>
      )}

      {isError && (
        <p className="text-sm text-red-500">Unable to load activity.</p>
      )}

      {!isLoading && !isError && auditLogs.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No activity recorded yet.
        </p>
      )}

      {!isLoading && !isError && auditLogs.length > 0 && (
        <div className="relative space-y-6">
          <div className="absolute left-2 top-2 bottom-2 w-px bg-[var(--border)]" />

          {auditLogs.map((log) => (
            <article key={log.id} className="relative pl-8">
              <span className="absolute left-0 top-1.5 h-4 w-4 rounded-full border-2 border-[var(--background)] bg-black dark:bg-white" />

              <div>
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                    {formatAction(log.action)}
                  </p>

                  <time
                    dateTime={log.created_at}
                    className="text-xs text-gray-500 dark:text-gray-400"
                  >
                    {new Date(log.created_at).toLocaleString()}
                  </time>
                </div>

                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  User #{log.user_id}
                </p>

                {log.details && (
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-gray-500 dark:text-gray-400">
                    {log.details}
                  </p>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
