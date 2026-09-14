"use client";

import { useGetIncidentsQuery } from "@/app/lib/services/api";
import Link from "next/link";
export default function IncidentPage() {
  const {
    data: incidents,
    isLoading,
    isError,
    refetch,
  } = useGetIncidentsQuery();

  if (isLoading) {
    return (
      <section className="relative z-10 animate-fade-in-up">
        <h1 className="text-3xl font-extrabold text-[var(--foreground)] tracking-tight">
          Incidents
        </h1>

        <div className="mt-6 rounded-2xl border border-[var(--border)] bg-[var(--background)] p-8 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-5 h-5 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm font-medium text-[var(--muted)]">
              Loading incidents...
            </p>
          </div>
        </div>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="relative z-10 animate-fade-in-up">
        <h1 className="text-3xl font-extrabold text-[var(--foreground)] tracking-tight">
          Incidents
        </h1>

        <div className="mt-6 rounded-2xl border border-red-500/20 bg-red-50 p-8 shadow-sm dark:bg-red-500/10">
          <div className="flex items-start gap-4">
            <div className="p-2 bg-red-100 rounded-lg dark:bg-red-500/20">
              <svg
                className="w-6 h-6 text-red-600 dark:text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                ></path>
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-800 dark:text-red-300">
                Unable to load incidents
              </h3>
              <p className="mt-1 text-sm text-red-600 dark:text-red-400/80">
                There was a problem fetching the data.
              </p>

              <button
                type="button"
                onClick={() => refetch()}
                className="mt-4 rounded-lg bg-red-100 px-5 py-2.5 text-sm font-medium text-red-700 transition-colors hover:bg-red-200 active:scale-95 border border-red-200 dark:bg-red-500/20 dark:text-red-200 dark:hover:bg-red-500/30 dark:border-red-500/30"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (!incidents || incidents.length === 0) {
    return (
      <section className="relative z-10 animate-fade-in-up">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-extrabold text-[var(--foreground)] tracking-tight">
              Incidents
            </h1>

            <p className="mt-2 text-sm font-medium text-[var(--muted)]">
              Track and investigate production incidents.
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-[var(--border)] bg-[var(--background)] p-16 text-center shadow-sm flex flex-col items-center justify-center">
          <div className="w-20 h-20 rounded-full bg-black/5 dark:bg-white/5 border border-[var(--border)] flex items-center justify-center mb-6 shadow-sm">
            <svg
              className="w-10 h-10 text-[var(--muted)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="1.5"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              ></path>
            </svg>
          </div>
          <h2 className="text-xl font-bold text-[var(--foreground)]">No incidents yet</h2>
          <p className="mt-2 text-[var(--muted)] max-w-sm mx-auto">
            There are currently no incidents available for your account. When
            they arrive, they&apos;ll show up here.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="relative z-10 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-[var(--foreground)]">
            Incidents
          </h1>
          <p className="mt-2 text-sm font-medium text-[var(--muted)]">
            Track and investigate production incidents.
          </p>
        </div>

        <button className="rounded-full bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-opacity hover:opacity-90 active:scale-95">
          + New Incident
        </button>
      </div>

      <div className="mt-8 overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--background)] shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left border-collapse">
            <thead className="bg-black/5 dark:bg-white/5 border-b border-[var(--border)]">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                  Title
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                  Severity
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                  Status
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                  Assigned To
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                  Created
                </th>
              </tr>
            </thead>

            <tbody className="divide-y divide-[var(--border)]">
              {incidents.map((incident) => (
                <tr
                  key={incident.id}
                  className="group transition-colors duration-200 hover:bg-black/5 dark:hover:bg-white/5"
                >
                  <td className="px-6 py-4">
                    <Link
                      href={`/incidents/${incident.id}`}
                      className="font-semibold text-[var(--foreground)] group-hover:text-[var(--accent)] transition-colors duration-200"
                    >
                      {incident.title}
                    </Link>
                    <div className="mt-1 max-w-md truncate text-sm text-[var(--muted)]">
                      {incident.description}
                    </div>
                  </td>

                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${
                        incident.severity === "critical" ||
                        incident.severity === "high"
                          ? "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 border border-red-200 dark:border-red-500/20"
                          : incident.severity === "medium"
                            ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-500/20"
                            : "bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20"
                      }`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          incident.severity === "critical" ||
                          incident.severity === "high"
                            ? "bg-red-500"
                            : incident.severity === "medium"
                              ? "bg-yellow-500"
                              : "bg-blue-500"
                        }`}
                      ></span>
                      {incident.severity}
                    </span>
                  </td>

                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${
                        incident.status === "resolved" ||
                        incident.status === "closed"
                          ? "bg-green-100 text-green-700 border-green-200 dark:bg-green-500/10 dark:text-green-400 dark:border-green-500/20"
                          : "bg-black/5 text-[var(--muted)] border-[var(--border)] dark:bg-white/5"
                      }`}
                    >
                      {incident.status}
                    </span>
                  </td>

                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded-full bg-[var(--border)] flex items-center justify-center">
                        <span className="text-[10px] font-semibold text-[var(--foreground)]">
                          {incident.assigned_to
                            ? `#${incident.assigned_to}`
                            : "?"}
                        </span>
                      </div>
                      <span className="text-sm text-[var(--foreground)]">
                        {incident.assigned_to ?? "Unassigned"}
                      </span>
                    </div>
                  </td>

                  <td className="px-6 py-4 text-sm text-[var(--muted)]">
                    {new Date(incident.created_at).toLocaleDateString(
                      undefined,
                      {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      },
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
