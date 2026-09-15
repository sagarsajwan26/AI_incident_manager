"use client";
import { useState } from "react";
import {
  useAddIncidentEvidenceMutation,
  useGetIncidentEvidenceQuery,
} from "@/app/lib/services/api";

type EvidenceSectionProps = {
  incidentId: number;
};

const EvidenceSection = ({ incidentId }: EvidenceSectionProps) => {
  const [evidenceType, setEvidenceType] = useState("log");
  const [evidenceContent, setEvidenceContent] = useState("");
  const {
    data: evidence,
    isLoading: isEvidenceLoading,
    isError: isEvidenceError,
    refetch: refetchEvidence,
  } = useGetIncidentEvidenceQuery(incidentId);

  const [addIncidentEvidence, { isLoading: isAddingEvidence }] =
    useAddIncidentEvidenceMutation();

  const handleAddEvidence = async () => {
    const content = evidenceContent.trim();

    if (!content) {
      return;
    }
    try {
      await addIncidentEvidence({
        incidentId,
        evidence_type: evidenceType,
        content,
      }).unwrap();
      setEvidenceContent("");
    } catch (error) {
      console.error("Failed to add evidence:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Add Evidence */}
      <section className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm">
        <header>
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Add Evidence
          </h2>

          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Provide details that may help investigate this incident.
          </p>
        </header>

        <div className="mt-5 space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-900 dark:text-gray-100">
              Evidence type
            </label>

            <select
              value={evidenceType}
              onChange={(event) => setEvidenceType(event.target.value)}
              className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-3 py-2 text-sm text-gray-900 dark:text-gray-100 outline-none focus:border-blue-500"
            >
              <option value="log">Log</option>
              <option value="error">Error</option>
              <option value="deployment">Deployment</option>
              <option value="commit">Commit</option>
              <option value="metric">Metric</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-900 dark:text-gray-100">
              Evidence content
            </label>

            <textarea
              value={evidenceContent}
              onChange={(event) => setEvidenceContent(event.target.value)}
              placeholder="Enter evidence details..."
              rows={4}
              className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-transparent px-3 py-2 text-sm text-gray-900 dark:text-gray-100 outline-none placeholder:text-gray-500 dark:text-gray-400 focus:border-blue-500"
            />
          </div>

          <button
            type="button"
            onClick={handleAddEvidence}
            disabled={isAddingEvidence || !evidenceContent.trim()}
            className="rounded-full bg-[var(--foreground)] px-4 py-2 text-sm font-semibold text-[var(--background)] transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isAddingEvidence ? "Adding..." : "Add Evidence"}
          </button>
        </div>
      </section>

      {/* Evidence List */}
      <section className="rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-6 shadow-sm">
        <header className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Evidence Log
            </h2>

            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Data collected for this incident.
            </p>
          </div>

          {!isEvidenceLoading && evidence && (
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {evidence.length} {evidence.length === 1 ? "item" : "items"}
            </span>
          )}
        </header>

        {isEvidenceLoading && (
          <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">
            Loading evidence...
          </p>
        )}

        {isEvidenceError && (
          <div className="mt-6">
            <p className="text-sm text-red-500">Unable to load evidence.</p>

            <button
              type="button"
              onClick={() => refetchEvidence()}
              className="mt-2 rounded-lg border border-gray-200 dark:border-gray-800 px-3 py-1.5 text-sm font-medium text-gray-900 dark:text-gray-100 transition hover:bg-black/5 dark:hover:bg-white/5"
            >
              Try again
            </button>
          </div>
        )}

        {!isEvidenceLoading && !isEvidenceError && evidence?.length === 0 && (
          <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">
            No evidence has been added yet.
          </p>
        )}

        {!isEvidenceLoading &&
          !isEvidenceError &&
          evidence &&
          evidence.length > 0 && (
            <div className="mt-6 space-y-3">
              {evidence.map((item) => (
                <article
                  key={item.id}
                  className="rounded-xl border border-gray-200 dark:border-gray-800 bg-black/5 p-4 dark:bg-white/5"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400">
                      {item.evidence_type}
                    </span>

                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                  </div>

                  <p className="mt-2 whitespace-pre-wrap text-sm text-gray-900 dark:text-gray-100">
                    {item.content}
                  </p>

                  {item.source && (
                    <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Source: {item.source}
                    </p>
                  )}
                </article>
              ))}
            </div>
          )}
      </section>
    </div>
  );
};

export default EvidenceSection;
