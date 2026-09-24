"use client";

import { useState } from "react";
import {
  useCollectGithubEvidenceMutation,
  useCollectGithubDeploymentEvidenceMutation,
} from "@/app/lib/services/api";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";
import { 
  DocumentArrowDownIcon, 
  ServerStackIcon, 
  FolderIcon, 
  UserCircleIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon 
} from "@heroicons/react/24/outline";

type GithubEvidenceCollectorProps = {
  incidentId?: number;
};

export default function GithubEvidenceCollector({
  incidentId,
}: GithubEvidenceCollectorProps) {
  const [incidentIdState, setIncidentIdState] = useState("");
  const [perPage, setPerPage] = useState(10);

  const activeIncidentId = incidentId ?? (parseInt(incidentIdState) || 0);

  const [message, setMessage] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const [collectGithubEvidence, { isLoading: isCollectingCommits }] =
    useCollectGithubEvidenceMutation();

  const [
    collectGithubDeploymentEvidence,
    { isLoading: isCollectingDeployments },
  ] = useCollectGithubDeploymentEvidenceMutation();

  const isLoading = isCollectingCommits || isCollectingDeployments;

  const validateForm = () => {
    if (!activeIncidentId) {
      setErrorMsg("Incident ID is required.");
      return false;
    }

    if (perPage < 1 || perPage > 100) {
      setErrorMsg("Items per page must be between 1 and 100.");
      return false;
    }

    return true;
  };

  const handleCollectCommits = async () => {
    setMessage("");
    setErrorMsg("");

    if (!validateForm()) {
      return;
    }

    try {
      const result = await collectGithubEvidence({
        incidentId: activeIncidentId,
        body: {
          per_page: perPage,
        },
      }).unwrap();

      setMessage(
        `Successfully collected ${result.length} commit ${
          result.length === 1 ? "evidence record" : "evidence records"
        }.`,
      );
    } catch (error) {
      setErrorMsg(getApiErrorMessage(error));
    }
  };

  const handleCollectDeployments = async () => {
    setMessage("");
    setErrorMsg("");

    if (!validateForm()) {
      return;
    }

    try {
      const result = await collectGithubDeploymentEvidence({
        incidentId: activeIncidentId,
        body: {
          per_page: perPage,
        },
      }).unwrap();

      setMessage(
        `Successfully collected ${result.length} deployment ${
          result.length === 1 ? "evidence record" : "evidence records"
        }.`,
      );
    } catch (error) {
      setErrorMsg(getApiErrorMessage(error));
    }
  };

  return (
    <section className="rounded-2xl glass-panel p-6 shadow-sm overflow-hidden relative border border-gray-200/50 dark:border-gray-800/50">
      {/* Decorative gradient blob */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
      
      <div className="mb-6 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-black/5 dark:bg-white/5 rounded-xl border border-black/10 dark:border-white/10 shadow-sm">
            <svg viewBox="0 0 24 24" aria-hidden="true" className="w-5 h-5 fill-black dark:fill-white"><path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.022A9.606 9.606 0 0 1 12 6.82c.85.004 1.705.114 2.504.336 1.909-1.29 2.747-1.022 2.747-1.022.546 1.379.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.161 22 16.418 22 12c0-5.523-4.477-10-10-10Z"></path></svg>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
              GitHub Evidence
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Import commits and deployments from GitHub.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6 relative z-10">
        {!incidentId && (
          <div className="space-y-1.5 border-b border-gray-200/50 pb-5 dark:border-gray-800/50">
            <label
              htmlFor="incident-id"
              className="block text-sm font-semibold text-gray-700 dark:text-gray-300"
            >
              Incident ID
            </label>
            <input
              id="incident-id"
              type="number"
              value={incidentIdState}
              onChange={(event) => setIncidentIdState(event.target.value)}
              placeholder="e.g. 123"
              disabled={isLoading}
              className="block w-full max-w-xs rounded-xl border border-gray-200/60 bg-black/[0.03] py-2.5 px-4 text-sm text-black outline-none transition placeholder:text-gray-400 focus:border-blue-500 focus:bg-white focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:bg-white/5 dark:text-white dark:focus:bg-black/50"
            />
          </div>
        )}



        {/* Per Page */}
        <div className="space-y-1.5 pt-1 border-t border-gray-200/50 dark:border-gray-800/50">
          <label
            htmlFor="github-per-page"
            className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mt-4"
          >
            Records to fetch: <span className="text-blue-600 dark:text-blue-400 font-bold ml-1">{perPage}</span>
          </label>
          <div className="flex items-center gap-4 pt-1">
            <input
              id="github-per-page"
              type="range"
              min={1}
              max={100}
              value={perPage}
              onChange={(event) => setPerPage(Number(event.target.value))}
              disabled={isLoading}
              className="h-2 w-full max-w-[200px] cursor-pointer appearance-none rounded-full bg-gray-200 dark:bg-gray-700 accent-blue-600 outline-none focus:ring-2 focus:ring-blue-500/30"
            />
          </div>
        </div>

        {/* Status Messages */}
        {errorMsg && (
          <div className="flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-50/50 p-4 text-sm text-red-600 dark:bg-red-500/10 dark:text-red-400 animate-fade-in-up">
            <ExclamationCircleIcon className="h-5 w-5 shrink-0 mt-0.5" />
            <p className="font-medium leading-relaxed">{errorMsg}</p>
          </div>
        )}

        {message && (
          <div className="flex items-start gap-3 rounded-xl border border-emerald-500/20 bg-emerald-50/50 p-4 text-sm text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400 animate-fade-in-up">
            <CheckCircleIcon className="h-5 w-5 shrink-0 mt-0.5" />
            <p className="font-medium leading-relaxed">{message}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid gap-3 sm:grid-cols-2 pt-3">
          <button
            type="button"
            onClick={handleCollectCommits}
            disabled={isLoading}
            className="group relative flex w-full items-center justify-center gap-2.5 overflow-hidden rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:bg-black hover:shadow-md active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black dark:hover:bg-gray-100"
          >
            {isCollectingCommits ? (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/20 border-t-white dark:border-black/20 dark:border-t-black" />
            ) : (
              <DocumentArrowDownIcon className="h-5 w-5 transition-transform group-hover:-translate-y-0.5" />
            )}
            <span>{isCollectingCommits ? "Fetching Commits..." : "Collect Commits"}</span>
          </button>

          <button
            type="button"
            onClick={handleCollectDeployments}
            disabled={isLoading}
            className="group relative flex w-full items-center justify-center gap-2.5 overflow-hidden rounded-xl border border-gray-300 bg-white px-4 py-3 text-sm font-semibold text-gray-700 shadow-sm transition-all hover:bg-gray-50 hover:shadow-md active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-black/20 dark:text-gray-300 dark:hover:bg-white/5"
          >
            {isCollectingDeployments ? (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-gray-400/30 border-t-gray-700 dark:border-white/20 dark:border-t-white" />
            ) : (
              <ServerStackIcon className="h-5 w-5 transition-transform group-hover:-translate-y-0.5" />
            )}
            <span>{isCollectingDeployments ? "Fetching Deployments..." : "Collect Deployments"}</span>
          </button>
        </div>
      </div>
    </section>
  );
}
