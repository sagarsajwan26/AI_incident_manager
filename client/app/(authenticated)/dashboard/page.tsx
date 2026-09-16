"use client";
import { useGetIncidentsQuery } from "@/app/lib/services/api";
import Link from "next/link";
export default function DashboardPage() {
  const { data: incidents = [], isLoading, isError } = useGetIncidentsQuery();
  const openCount = incidents.filter(
    (incident) => incident.status === "open",
  ).length;

  const investigatingCount = incidents.filter(
    (incident) => incident.status === "investigating",
  ).length;

  const containedCount = incidents.filter(
    (incident) => incident.status === "contained",
  ).length;

  const resolvedCount = incidents.filter(
    (incident) => incident.status === "resolved",
  ).length;

  const criticalCount = incidents.filter(
    (incident) => incident.severity === "critical",
  ).length;
  const recentIncidents = [...incidents]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )
    .slice(0, 5);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-white px-8 py-12 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
        <p className="text-gray-500 dark:text-gray-400">Loading dashboard...</p>
      </main>
    );
  }

  if (isError) {
    return (
      <main className="min-h-screen bg-white px-8 py-12 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
        <p className="text-red-500">Unable to load incident dashboard.</p>
      </main>
    );
  }
  return (
    <main className="min-h-screen bg-white px-8 py-12 text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-10">
          <div className="mb-4 inline-flex items-center rounded-full border border-gray-200 bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 shadow-sm dark:border-gray-800 dark:bg-gray-950 dark:text-gray-400">
            Operations Overview
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight">
            AI Incident Manager
          </h1>

          <p className="mt-2 text-gray-500 dark:text-gray-400">
            Monitor incidents, investigations, and response activity.
          </p>
        </div>

        {/* Statistics */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <StatCard label="Open" value={openCount} />

          <StatCard label="Investigating" value={investigatingCount} />

          <StatCard label="Contained" value={containedCount} />

          <StatCard label="Resolved" value={resolvedCount} />

          <StatCard label="Critical" value={criticalCount} />
        </section>

        {/* Recent Incidents */}
        <section className="mt-10">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Recent Incidents</h2>

              <p className="text-sm text-gray-500 dark:text-gray-400">
                Latest incidents reported in your organization.
              </p>
            </div>

            <Link
              href="/incidents"
              className="text-sm font-semibold text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
            >
              View all →
            </Link>
          </div>

          <div className="overflow-hidden rounded-2xl border border-gray-200/50 dark:border-gray-800/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm shadow-xl shadow-gray-200/20 dark:shadow-black/20">
            {recentIncidents.length === 0 ? (
              <div className="p-12 text-center text-sm text-gray-500 dark:text-gray-400 font-medium">
                No incidents found. You're all clear!
              </div>
            ) : (
              <div className="divide-y divide-gray-200/50 dark:divide-gray-800/50">
                {recentIncidents.map((incident) => (
                  <Link
                    key={incident.id}
                    href={`/incidents/${incident.id}`}
                    className="block p-5 transition-colors hover:bg-white dark:hover:bg-gray-800"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 transition-colors">{incident.title}</h3>

                          <SeverityBadge severity={incident.severity} />
                        </div>

                        <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400 line-clamp-1">
                          {incident.description}
                        </p>
                      </div>

                      <StatusBadge status={incident.status} />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-gray-200/50 dark:border-gray-800/50 bg-white dark:bg-gray-900 p-6 shadow-sm transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-gray-200 dark:hover:shadow-black/50">
      <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
        {label}
      </p>

      <p className="mt-3 text-4xl font-extrabold">{value}</p>
    </div>
  );
}

function SeverityBadge({
  severity,
}: {
  severity: "low" | "medium" | "high" | "critical";
}) {
  const styles = {
    low: "bg-gray-500/10 text-gray-700 dark:text-gray-300 border border-gray-500/20",
    medium: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border border-blue-500/20",
    high: "bg-orange-500/10 text-orange-700 dark:text-orange-400 border border-orange-500/20",
    critical: "bg-red-500/10 text-red-700 dark:text-red-400 border border-red-500/20",
  };

  return (
    <span
      className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${styles[severity]}`}
    >
      {severity}
    </span>
  );
}

function StatusBadge({
  status,
}: {
  status: "open" | "investigating" | "contained" | "resolved" | "closed";
}) {
  return (
    <span className="rounded-full bg-gray-500/10 border border-gray-500/20 px-3 py-1.5 text-xs font-semibold capitalize text-gray-700 dark:text-gray-300">
      {status}
    </span>
  );
}
