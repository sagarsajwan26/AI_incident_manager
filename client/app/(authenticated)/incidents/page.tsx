"use client";

import { type Incident, useGetIncidentsQuery } from "@/app/lib/services/api";
import Link from "next/link";
import { useState } from "react";

const severityStyles = {
  low: {
    badge:
      "bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400 border border-blue-200 dark:border-blue-500/20",
    dot: "bg-blue-500",
  },
  medium: {
    badge:
      "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-500/20",
    dot: "bg-yellow-500",
  },
  high: {
    badge:
      "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 border border-red-200 dark:border-red-500/20",
    dot: "bg-red-500",
  },
  critical: {
    badge:
      "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 border border-red-200 dark:border-red-500/20",
    dot: "bg-red-500",
  },
} satisfies Record<
  "low" | "medium" | "high" | "critical",
  { badge: string; dot: string }
>;
export default function IncidentPage() {
  const {
    data: incidents,
    isLoading,
    isError,
    refetch,
  } = useGetIncidentsQuery();

  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<
    Incident["severity"] | "all"
  >("all");
  const [statusFilter, setStatusFilter] = useState<Incident["status"] | "all">(
    "all",
  );

  const normalizedSearch = search.trim().toLowerCase();
  const filteredIncidents =
    incidents?.filter((incident) => {
      const matchesSearch =
        !normalizedSearch ||
        incident.title.toLowerCase().includes(normalizedSearch) ||
        incident.description.toLowerCase().includes(normalizedSearch);
      const matchesStatus =
        statusFilter === "all" || incident.status === statusFilter;

      const matchesSeverity =
        severityFilter === "all" || incident.severity === severityFilter;

      return matchesSearch && matchesStatus && matchesSeverity;
    }) ?? [];
  const hasActiveFilters =
    search.trim() !== "" || statusFilter !== "all" || severityFilter !== "all";

  if (isLoading) {
    return (
      <section className="relative z-10 animate-fade-in-up">
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-gray-100 tracking-tight">
          Incidents
        </h1>

        <div className="mt-6 rounded-2xl border border-gray-200/50 dark:border-gray-800/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm p-8 shadow-sm">
          <div className="flex items-center space-x-3">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
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
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-gray-100 tracking-tight">
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
            <h1 className="text-3xl font-extrabold text-gray-900 dark:text-gray-100 tracking-tight">
              Incidents
            </h1>

            <p className="mt-2 text-sm font-medium text-gray-500 dark:text-gray-400">
              Track and investigate production incidents.
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-16 text-center shadow-sm flex flex-col items-center justify-center">
          <div className="w-20 h-20 rounded-full bg-black/5 dark:bg-white/5 border border-gray-200 dark:border-gray-800 flex items-center justify-center mb-6 shadow-sm">
            <svg
              className="w-10 h-10 text-gray-500 dark:text-gray-400"
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
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
            No incidents yet
          </h2>
          <p className="mt-2 text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
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
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100">
            Incidents
          </h1>
          <p className="mt-2 text-sm font-medium text-gray-500 dark:text-gray-400">
            Track and investigate production incidents.
          </p>
        </div>

        <Link
          href={"/incidents/new"}
          className="rounded-full bg-blue-600 dark:bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-opacity hover:opacity-90 active:scale-95"
        >
          + New Incident
        </Link>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-3">
        {/* Search */}
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search incidents..."
          className="rounded-xl border border-gray-200/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm px-4 py-2.5 text-sm text-gray-900 outline-none transition-all placeholder:text-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-gray-800/50 dark:text-gray-100 dark:placeholder:text-gray-600 shadow-sm hover:border-gray-300 dark:hover:border-gray-700"
        />

        {/* Status */}
        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value as Incident["status"] | "all")
          }
          className="rounded-xl border border-gray-200/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm px-4 py-2.5 text-sm text-gray-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-gray-800/50 dark:text-gray-100 shadow-sm hover:border-gray-300 dark:hover:border-gray-700"
        >
          <option value="all">All statuses</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="contained">Contained</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>

        {/* Severity */}
        <select
          value={severityFilter}
          onChange={(event) =>
            setSeverityFilter(
              event.target.value as Incident["severity"] | "all",
            )
          }
          className="rounded-xl border border-gray-200/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm px-4 py-2.5 text-sm text-gray-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-gray-800/50 dark:text-gray-100 shadow-sm hover:border-gray-300 dark:hover:border-gray-700"
        >
          <option value="all">All severities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Showing {filteredIncidents.length} of {incidents?.length ?? 0}{" "}
          incidents
        </p>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={() => {
              setSearch("");
              setStatusFilter("all");
              setSeverityFilter("all");
            }}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 hover:underline transition-colors"
          >
            Clear filters
          </button>
        )}
      </div>

      <div className="mt-8 overflow-hidden rounded-2xl border border-gray-200/50 dark:border-gray-800/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm shadow-xl shadow-gray-200/20 dark:shadow-black/20">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left border-collapse">
            <thead className="bg-gray-50/50 dark:bg-gray-900/50 border-b border-gray-200/50 dark:border-gray-800/50">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Title
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Severity
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Status
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Assigned To
                </th>
                <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
              {filteredIncidents?.map((incident) => {
                const style =
                  severityStyles[incident.severity] || severityStyles.low;
                return (
                  <tr
                    key={incident.id}
                    className="group transition-colors hover:bg-black/[0.02] dark:hover:bg-white/[0.02]"
                  >
                    <td className="px-6 py-4">
                      <Link
                        href={`/incidents/${incident.id}`}
                        className="block"
                      >
                        <span className="font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {incident.title}
                        </span>
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <div
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${style.badge}`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${style.dot}`}
                        ></span>
                        <span className="capitalize">{incident.severity}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="capitalize text-gray-700 dark:text-gray-300">
                        {incident.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-gray-700 dark:text-gray-300">
                        {incident.assigned_to || "Unassigned"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {new Date(incident.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })}
              {filteredIncidents?.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="px-6 py-8 text-center text-gray-500 dark:text-gray-400"
                  >
                    No incidents found matching your criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
