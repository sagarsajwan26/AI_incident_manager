"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useGetIncidentInvestigationQuery } from "@/app/lib/services/api";

const rootCauseStatusStyles = {
  confirmed: "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400 border border-green-200 dark:border-green-500/20",
  probable: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400 border border-yellow-200 dark:border-yellow-500/20",
  unknown: "bg-black/5 text-[var(--muted)] border border-[var(--border)] dark:bg-white/5",
};

const InvestigationDetailsPage = () => {
  const params = useParams();
  const incidentId = Number(params.incidentID);
  const investigationId = Number(params.investigationsID);
  const validIds = Number.isInteger(incidentId) && Number.isInteger(investigationId);

  const {
    data: investigation,
    isLoading,
    isError,
  } = useGetIncidentInvestigationQuery(
    { incidentId, investigationId },
    { skip: !validIds },
  );

  if (!validIds) {
    return (
      <main className="space-y-6 p-8">
        <nav>
          <Link
            href="/incidents"
            className="text-sm font-medium text-[var(--accent)] hover:underline"
          >
            ← Back to incidents
          </Link>
        </nav>

        <section className="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-500/20 dark:bg-red-500/10 shadow-sm">
          <h1 className="text-lg font-bold text-red-600 dark:text-red-400">
            Invalid investigation URL
          </h1>
        </section>
      </main>
    );
  }
  
  if (isLoading) {
    return (
      <main className="flex min-h-[400px] items-center justify-center p-8">
        <p className="text-[var(--muted)] font-medium">Loading investigation...</p>
      </main>
    );
  }

  if (isError || !investigation) {
    return (
      <main className="space-y-6 p-8">
        <nav>
          <Link
            href={`/incidents/${incidentId}`}
            className="text-sm font-medium text-[var(--accent)] hover:underline"
          >
            ← Back to incident
          </Link>
        </nav>

        <section className="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-500/20 dark:bg-red-500/10 shadow-sm">
          <h1 className="text-lg font-bold text-red-600 dark:text-red-400">
            Investigation not found
          </h1>

          <p className="mt-2 text-sm text-red-500 dark:text-red-300">
            This investigation does not exist or is not accessible.
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className="space-y-6">
      <nav>
        <Link
          href={`/incidents/${incidentId}`}
          className="text-sm font-medium text-[var(--accent)] hover:underline"
        >
          ← Back to incident
        </Link>
      </nav>

      {/* Header */}
      <header className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-medium text-[var(--muted)]">
              Investigation #{investigation.id}
            </p>

            <h1 className="mt-1 text-2xl font-bold text-[var(--foreground)]">AI Investigation</h1>

            <p className="mt-2 text-sm font-medium text-[var(--muted)]">
              Created {new Date(investigation.created_at).toLocaleString()}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${
                rootCauseStatusStyles[investigation.root_cause_status]
              }`}
            >
              {investigation.root_cause_status}
            </span>

            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-500/20">
              {Math.round(investigation.confidence * 100)}% confidence
            </span>
          </div>
        </div>
      </header>

      {/* Summary */}
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
        <h2 className="text-lg font-bold text-[var(--foreground)]">Summary</h2>
        <p className="mt-3 text-sm leading-6 text-[var(--muted)] whitespace-pre-wrap">{investigation.summary}</p>
      </section>

      {/* Root Cause */}
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
        <h2 className="text-lg font-bold text-[var(--foreground)]">Likely Root Cause</h2>
        <p className="mt-3 text-sm leading-6 text-[var(--muted)] whitespace-pre-wrap">
          {investigation.likely_root_cause}
        </p>
      </section>

      {/* Impact */}
      <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
        <h2 className="text-lg font-bold text-[var(--foreground)]">Impact</h2>
        <p className="mt-3 text-sm leading-6 text-[var(--muted)] whitespace-pre-wrap">{investigation.impact}</p>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Evidence */}
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
          <h2 className="text-lg font-bold text-[var(--foreground)]">AI Evidence</h2>
          {(!investigation.evidence || investigation.evidence.length === 0) ? (
            <p className="mt-3 text-sm text-[var(--muted)]">
              No evidence was identified.
            </p>
          ) : (
            <ul className="mt-4 space-y-3">
              {investigation.evidence.map((item, index) => (
                <li
                  key={index}
                  className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4 text-sm leading-6 text-[var(--foreground)]"
                >
                  {item}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Recommended Actions */}
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
          <h2 className="text-lg font-bold text-[var(--foreground)]">Recommended Actions</h2>
          {(!investigation.recommended_actions || investigation.recommended_actions.length === 0) ? (
            <p className="mt-3 text-sm text-[var(--muted)]">
              No recommended actions were provided.
            </p>
          ) : (
            <ol className="mt-4 space-y-3">
              {investigation.recommended_actions.map((action, index) => (
                <li
                  key={index}
                  className="flex gap-3 rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4"
                >
                  <span className="font-bold text-[var(--accent)]">
                    {index + 1}.
                  </span>
                  <span className="text-sm leading-6 text-[var(--foreground)]">
                    {action}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Unknowns */}
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
          <h2 className="text-lg font-bold text-[var(--foreground)]">Unknowns</h2>
          {(!investigation.unknowns || investigation.unknowns.length === 0) ? (
            <p className="mt-3 text-sm text-[var(--muted)]">
              No unknowns were reported.
            </p>
          ) : (
            <ul className="mt-4 space-y-3">
              {investigation.unknowns.map((unknown, index) => (
                <li
                  key={index}
                  className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4 text-sm leading-6 text-[var(--foreground)]"
                >
                  {unknown}
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Metadata */}
        <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
          <h2 className="text-lg font-bold text-[var(--foreground)]">Investigation Metadata</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <article className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4">
              <h3 className="text-xs font-semibold text-[var(--muted)]">Provider</h3>
              <p className="mt-1 text-sm font-medium text-[var(--foreground)]">
                {investigation.provider}
              </p>
            </article>

            <article className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4">
              <h3 className="text-xs font-semibold text-[var(--muted)]">Model</h3>
              <p className="mt-1 text-sm font-medium text-[var(--foreground)]">{investigation.model}</p>
            </article>

            <article className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4">
              <h3 className="text-xs font-semibold text-[var(--muted)]">Investigation ID</h3>
              <p className="mt-1 text-sm font-medium text-[var(--foreground)]">#{investigation.id}</p>
            </article>
          </div>
        </section>
      </div>
    </main>
  );
};

export default InvestigationDetailsPage;
