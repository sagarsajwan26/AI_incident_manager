"use client";
import { useState } from "react";
import {
  useAddIncidentEvidenceMutation,
  useGetIncidentEvidenceQuery,
} from "@/app/lib/services/api";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";

type EvidenceSectionProps = {
  incidentId: number;
};

const EvidenceSection = ({ incidentId }: EvidenceSectionProps) => {
  const [evidenceType, setEvidenceType] = useState("log");
  const [evidenceContent, setEvidenceContent] = useState("");
  const [addError, setAddError] = useState<string | null>(null);
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
      setAddError(null);
      await addIncidentEvidence({
        incidentId,
        evidence_type: evidenceType,
        content,
      }).unwrap();
      setEvidenceContent("");
    } catch (error) {
      setAddError(getApiErrorMessage(error));
    }
  };

  return (
    <div className="space-y-6">
      {/* Add Evidence */}
      <section className="rounded-2xl glass-panel p-6 shadow-sm overflow-hidden relative border border-gray-200/50 dark:border-gray-800/50">
        <header className="mb-6">
          <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Add Evidence
          </h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Provide details manually that may help investigate this incident.
          </p>
        </header>

        <div className="space-y-4 animate-fade-in">
          <div>
            <label className="mb-1.5 block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Evidence type
            </label>
            <select
              value={evidenceType}
              onChange={(event) => setEvidenceType(event.target.value)}
              className="w-full rounded-xl border border-gray-200/60 bg-black/[0.03] px-3 py-2.5 text-sm text-black outline-none transition focus:border-blue-500 focus:bg-white focus:ring-1 focus:ring-blue-500 dark:border-white/10 dark:bg-white/5 dark:text-white dark:focus:bg-black/50"
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
            <label className="mb-1.5 block text-sm font-semibold text-gray-700 dark:text-gray-300">
              Evidence content
            </label>
            <textarea
              value={evidenceContent}
              onChange={(event) => setEvidenceContent(event.target.value)}
              placeholder="Enter evidence details..."
              rows={4}
              className="w-full rounded-xl border border-gray-200/60 bg-black/[0.03] px-3 py-2.5 text-sm text-black outline-none placeholder:text-gray-400 transition focus:border-blue-500 focus:bg-white focus:ring-1 focus:ring-blue-500 dark:border-white/10 dark:bg-white/5 dark:text-white dark:focus:bg-black/50"
            />
          </div>

          <div className="pt-2">
            {addError && (
              <p className="mb-3 text-sm text-red-500">
                {addError}
              </p>
            )}
            <button
              type="button"
              onClick={handleAddEvidence}
              disabled={isAddingEvidence || !evidenceContent.trim()}
              className="w-full rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white transition-all hover:bg-black active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-gray-100"
            >
              {isAddingEvidence ? "Adding..." : "Add Evidence"}
            </button>
          </div>
        </div>
      </section>

      {/* Evidence List */}
      <section className="rounded-2xl glass-panel p-6 shadow-sm border border-gray-200/50 dark:border-gray-800/50">
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
          <div className="mt-6 flex justify-center py-4">
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-gray-400/30 border-t-gray-700 dark:border-white/20 dark:border-t-white" />
          </div>
        )}

        {isEvidenceError && (
          <div className="mt-6 flex flex-col items-center justify-center py-6 text-center">
            <p className="text-sm text-red-500">Unable to load evidence.</p>
            <button
              type="button"
              onClick={() => refetchEvidence()}
              className="mt-3 rounded-lg border border-gray-200/50 px-4 py-2 text-sm font-medium text-black transition hover:bg-black/5 dark:border-gray-800/50 dark:text-white dark:hover:bg-white/5"
            >
              Try again
            </button>
          </div>
        )}

        {!isEvidenceLoading && !isEvidenceError && evidence?.length === 0 && (
          <div className="mt-6 flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300/50 bg-black/5 py-10 dark:border-gray-700/50 dark:bg-white/5">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No evidence has been added yet.
            </p>
          </div>
        )}

        {!isEvidenceLoading &&
          !isEvidenceError &&
          evidence &&
          evidence.length > 0 && (
            <div className="mt-6 space-y-3">
              {evidence.map((item) => (
                <article
                  key={item.id}
                  className="rounded-xl border border-transparent bg-black/5 p-4 transition-colors hover:bg-black/10 dark:bg-white/5 dark:hover:bg-white/10"
                >
                  <div className="flex items-center justify-between gap-4">
                    <span className="inline-flex items-center rounded-md bg-white px-2 py-1 text-xs font-bold uppercase tracking-wider text-black shadow-sm dark:bg-gray-800 dark:text-white">
                      {item.evidence_type}
                    </span>

                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                  </div>

                  <p className="mt-3 whitespace-pre-wrap text-sm text-gray-900 dark:text-gray-100">
                    {item.content}
                  </p>

                  {item.source && (
                    <div className="mt-3 flex items-center gap-1.5 pt-3 border-t border-black/10 dark:border-white/10">
                      <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                        Source:
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-300 break-all">
                        {item.source}
                      </span>
                    </div>
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
