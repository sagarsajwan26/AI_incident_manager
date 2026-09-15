"use client";
import React from "react";

import Link from "next/link";
import { useGetIncidentInvestigationsQuery } from "@/app/lib/services/api";

type InvestigationHistoryProps = {
  incidentId: number;
};

export const InvestigationHistory = ({
  incidentId,
}: InvestigationHistoryProps) => {
  const {
    data: investigations = [],
    isLoading,
    isError,
  } = useGetIncidentInvestigationsQuery(incidentId);

  return (
    <section className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm">
      <header className="mb-5">
        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
          Investigation History
        </h2>

        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Previous AI investigations for this incident.
        </p>
      </header>

      {isLoading && (
        <p className="text-sm text-gray-500 dark:text-gray-400">Loading investigations...</p>
      )}

      {isError && (
        <p className="text-sm text-red-500">Failed to load history.</p>
      )}

      {!isLoading && !isError && investigations.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No previous investigations found.
        </p>
      )}

      {!isLoading && !isError && investigations.length > 0 && (
        <div className="space-y-3">
          {investigations.map((item) => (
            <Link
              key={item.id}
              href={`/incidents/${incidentId}/investigations/${item.id}`}
              className="block rounded-xl border border-gray-200 dark:border-gray-800 bg-black/5 p-4 transition-colors hover:border-[var(--accent)] dark:bg-white/5"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="font-semibold text-gray-900 dark:text-gray-100">
                  Investigation #{item.id}
                </p>

                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>

              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {new Date(item.created_at).toLocaleString()}
              </p>

              <p className="mt-2 line-clamp-2 text-sm text-gray-900 dark:text-gray-100">
                {item.summary}
              </p>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
};
