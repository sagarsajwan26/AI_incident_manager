"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

import {
  useGetIncidentEvidenceQuery,
  useGetIncidentInvestigationsQuery,
  useGetIncidentQuery,
  useInvestigateIncidentMutation,
  useAddIncidentEvidenceMutation,
  useUpdateIncidentStatusMutation,
  useGetIncidentCommentsQuery,
  useAddIncidentCommentMutation,
  type Incident,
} from "@/app/lib/services/api";

const severityStyles = {
  low: "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400 border-green-200 dark:border-green-500/20",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400 border-yellow-200 dark:border-yellow-500/20",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-500/10 dark:text-orange-400 border-orange-200 dark:border-orange-500/20",
  critical: "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400 border-red-200 dark:border-red-500/20",
};

const statusStyles = {
  open: "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20",
  investigating: "bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/20",
  contained: "bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-500/10 dark:text-yellow-400 dark:border-yellow-500/20",
  resolved: "bg-green-100 text-green-700 border-green-200 dark:bg-green-500/10 dark:text-green-400 dark:border-green-500/20",
  closed: "bg-black/5 text-[var(--muted)] border-[var(--border)] dark:bg-white/5",
};

export default function IncidentDetailPage() {
  const params = useParams();
  const incidentId = Number(params.incidentID);

  const { data: incident, isLoading, isError } = useGetIncidentQuery(incidentId, {
    skip: !Number.isInteger(incidentId),
  });

  const {
    data: evidence,
    isLoading: isEvidenceLoading,
    isError: isEvidenceError,
    refetch: refetchEvidence,
  } = useGetIncidentEvidenceQuery(incidentId, {
    skip: !Number.isInteger(incidentId),
  });

  const [addIncidentEvidence, { isLoading: isAddingEvidence }] = useAddIncidentEvidenceMutation();
  const [evidenceType, setEvidenceType] = useState("log");
  const [evidenceContent, setEvidenceContent] = useState("");

  const handleAddEvidence = async () => {
    if (!evidenceContent.trim()) return;
    try {
      await addIncidentEvidence({
        incidentId,
        evidence_type: evidenceType,
        content: evidenceContent.trim(),
      }).unwrap();
      setEvidenceContent("");
    } catch (error) {
      console.error("Failed to add evidence:", error);
    }
  };

  const {
    data: investigations = [],
    isLoading: isInvestigationsLoading,
    isError: isInvestigationsError,
  } = useGetIncidentInvestigationsQuery(incidentId, {
    skip: !Number.isInteger(incidentId),
  });

  const [
    investigateIncident,
    { data: investigation, isLoading: isInvestigating, isError: isInvestigationError },
  ] = useInvestigateIncidentMutation();

  const handleInvestigate = async () => {
    try {
      await investigateIncident(incidentId).unwrap();
    } catch (error) {
      console.error("Investigation failed:", error);
    }
  };

  const [updateIncidentStatus, { isLoading: isUpdatingStatus }] = useUpdateIncidentStatusMutation();

  const handleStatusChange = async (newStatus: Incident["status"]) => {
    try {
      await updateIncidentStatus({
        incidentId,
        status: newStatus,
      }).unwrap();
    } catch (error) {
      console.error("Failed to update incident status:", error);
    }
  };

  const { data: comments = [], isLoading: isLoadingComments } = useGetIncidentCommentsQuery(incidentId);
  const [addIncidentComment, { isLoading: isAddingComment }] = useAddIncidentCommentMutation();
  const [comment, setComment] = useState("");

  const handleAddComment = async () => {
    const trimmedContent = comment.trim();
    if (!trimmedContent) return;
    try {
      await addIncidentComment({
        incidentId,
        content: trimmedContent,
      }).unwrap();
      setComment("");
    } catch (error) {
      console.error("Failed to add comment:", error);
    }
  };

  if (!Number.isInteger(incidentId)) {
    return (
      <main className="p-8">
        <p className="text-red-500">Invalid incident ID.</p>
      </main>
    );
  }

  if (isLoading) {
    return (
      <main className="p-8">
        <p className="text-[var(--muted)]">Loading incident...</p>
      </main>
    );
  }

  if (isError || !incident) {
    return (
      <main className="p-8">
        <p className="text-red-500">Unable to load incident.</p>
      </main>
    );
  }

  return (
    <main className="space-y-6">
      <nav>
        <Link
          href="/incidents"
          className="text-sm font-medium text-[var(--accent)] hover:underline"
        >
          ← Back to incidents
        </Link>
      </nav>

      {isInvestigationError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-500/20 dark:bg-red-500/10">
          <p className="text-sm font-medium text-red-600 dark:text-red-400">
            Investigation failed. Please try again.
          </p>
        </div>
      )}

      {/* Incident Header & Overview */}
      <header className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-medium text-[var(--muted)]">Incident #{incident.id}</p>
            <h1 className="mt-1 text-2xl font-bold text-[var(--foreground)]">
              {incident.title}
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
                severityStyles[incident.severity]
              }`}
            >
              {incident.severity}
            </span>

            <span
              className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold capitalize ${
                statusStyles[incident.status]
              }`}
            >
              {incident.status}
            </span>

            <select
              value={incident.status}
              onChange={(event) =>
                handleStatusChange(event.target.value as Incident["status"])
              }
              disabled={isUpdatingStatus}
              aria-label="Update incident status"
              className="rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-sm font-medium text-[var(--foreground)] outline-none transition focus:border-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="contained">Contained</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>

            <button
              type="button"
              onClick={handleInvestigate}
              disabled={isInvestigating}
              className="rounded-full bg-[var(--accent)] px-4 py-1.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isInvestigating ? "Investigating..." : "Investigate"}
            </button>
          </div>
        </div>

        <div className="mt-6">
          <h2 className="text-sm font-semibold text-[var(--foreground)]">Description</h2>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-[var(--muted)]">
            {incident.description}
          </p>
        </div>
      </header>

      {/* Incident Metadata */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-5 shadow-sm">
          <h3 className="text-xs font-semibold text-[var(--muted)]">Reported by</h3>
          <p className="mt-1 text-sm font-medium text-[var(--foreground)]">
            User #{incident.reported_by}
          </p>
        </article>

        <article className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-5 shadow-sm">
          <h3 className="text-xs font-semibold text-[var(--muted)]">Assigned to</h3>
          <p className="mt-1 text-sm font-medium text-[var(--foreground)]">
            {incident.assigned_to ? `User #${incident.assigned_to}` : "Unassigned"}
          </p>
        </article>

        <article className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-5 shadow-sm">
          <h3 className="text-xs font-semibold text-[var(--muted)]">Created</h3>
          <p className="mt-1 text-sm font-medium text-[var(--foreground)]">
            {new Date(incident.created_at).toLocaleString()}
          </p>
        </article>

        <article className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-5 shadow-sm">
          <h3 className="text-xs font-semibold text-[var(--muted)]">Last updated</h3>
          <p className="mt-1 text-sm font-medium text-[var(--foreground)]">
            {new Date(incident.updated_at).toLocaleString()}
          </p>
        </article>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Evidence Column */}
        <div className="space-y-6">
          {/* Add Evidence */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
            <header>
              <h2 className="text-lg font-bold text-[var(--foreground)]">Add Evidence</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Provide details that may help investigate this incident.
              </p>
            </header>

            <div className="mt-5 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-[var(--foreground)]">
                  Evidence type
                </label>
                <select
                  value={evidenceType}
                  onChange={(event) => setEvidenceType(event.target.value)}
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm text-[var(--foreground)] outline-none focus:border-[var(--accent)]"
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
                <label className="mb-1.5 block text-sm font-medium text-[var(--foreground)]">
                  Evidence content
                </label>
                <textarea
                  value={evidenceContent}
                  onChange={(event) => setEvidenceContent(event.target.value)}
                  placeholder="Enter evidence details..."
                  rows={4}
                  className="w-full rounded-lg border border-[var(--border)] bg-transparent px-3 py-2 text-sm text-[var(--foreground)] outline-none placeholder:text-[var(--muted)] focus:border-[var(--accent)]"
                />
              </div>

              <button
                type="button"
                onClick={handleAddEvidence}
                disabled={isAddingEvidence || !evidenceContent.trim()}
                className="rounded-full bg-[var(--foreground)] text-[var(--background)] px-4 py-2 text-sm font-semibold transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isAddingEvidence ? "Adding..." : "Add Evidence"}
              </button>
            </div>
          </section>

          {/* Evidence List */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
            <header className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-[var(--foreground)]">Evidence Log</h2>
                <p className="mt-1 text-sm text-[var(--muted)]">
                  Data collected for this incident.
                </p>
              </div>
              {!isEvidenceLoading && evidence && (
                <span className="text-sm font-medium text-[var(--muted)]">
                  {evidence.length} {evidence.length === 1 ? "item" : "items"}
                </span>
              )}
            </header>

            {isEvidenceLoading && (
              <p className="mt-6 text-sm text-[var(--muted)]">Loading evidence...</p>
            )}

            {isEvidenceError && (
              <div className="mt-6">
                <p className="text-sm text-red-500">Unable to load evidence.</p>
                <button
                  type="button"
                  onClick={() => refetchEvidence()}
                  className="mt-2 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm font-medium text-[var(--foreground)] transition hover:bg-black/5 dark:hover:bg-white/5"
                >
                  Try again
                </button>
              </div>
            )}

            {!isEvidenceLoading && !isEvidenceError && evidence?.length === 0 && (
              <p className="mt-6 text-sm text-[var(--muted)]">
                No evidence has been added yet.
              </p>
            )}

            {!isEvidenceLoading && !isEvidenceError && evidence && evidence.length > 0 && (
              <div className="mt-6 space-y-3">
                {evidence.map((item) => (
                  <article
                    key={item.id}
                    className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <span className="text-xs font-bold uppercase tracking-wider text-[var(--accent)]">
                        {item.evidence_type}
                      </span>
                      <span className="text-xs text-[var(--muted)]">
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="mt-2 whitespace-pre-wrap text-sm text-[var(--foreground)]">
                      {item.content}
                    </p>
                    {item.source && (
                      <p className="mt-2 text-xs text-[var(--muted)]">Source: {item.source}</p>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* History and Comments Column */}
        <div className="space-y-6">
          {/* Investigation History */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
            <header className="mb-5">
              <h2 className="text-lg font-bold text-[var(--foreground)]">
                Investigation History
              </h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Previous AI investigations for this incident.
              </p>
            </header>

            {isInvestigationsLoading && (
              <p className="text-sm text-[var(--muted)]">Loading investigations...</p>
            )}

            {isInvestigationsError && (
              <p className="text-sm text-red-500">Failed to load history.</p>
            )}

            {!isInvestigationsLoading && !isInvestigationsError && investigations.length === 0 && (
              <p className="text-sm text-[var(--muted)]">
                No previous investigations found.
              </p>
            )}

            {!isInvestigationsLoading && !isInvestigationsError && investigations.length > 0 && (
              <div className="space-y-3">
                {investigations.map((item) => (
                  <Link
                    key={item.id}
                    href={`/incidents/${incidentId}/investigations/${item.id}`}
                    className="block rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4 transition-colors hover:border-[var(--accent)]"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="font-semibold text-[var(--foreground)]">
                        Investigation #{item.id}
                      </p>
                      <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                        {Math.round(item.confidence * 100)}%
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                    <p className="mt-2 text-sm text-[var(--foreground)] line-clamp-2">
                      {item.summary}
                    </p>
                  </Link>
                ))}
              </div>
            )}
          </section>

          {/* Comments */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-6 shadow-sm">
            <header className="mb-5">
              <h2 className="text-lg font-bold text-[var(--foreground)]">Discussion</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Incident updates and team notes.
              </p>
            </header>

            <div className="space-y-4">
              {isLoadingComments ? (
                <p className="text-sm text-[var(--muted)]">Loading comments...</p>
              ) : comments.length === 0 ? (
                <p className="text-sm text-[var(--muted)]">No comments yet.</p>
              ) : (
                comments.map((item) => (
                  <article
                    key={item.id}
                    className="rounded-xl border border-[var(--border)] bg-black/5 dark:bg-white/5 p-4"
                  >
                    <p className="text-sm text-[var(--foreground)]">
                      {item.content}
                    </p>
                    <p className="mt-2 text-xs text-[var(--muted)]">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </article>
                ))
              )}
            </div>

            <div className="mt-6 border-t border-[var(--border)] pt-5">
              <textarea
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Add a comment..."
                rows={3}
                className="w-full rounded-lg border border-[var(--border)] bg-transparent px-3 py-2 text-sm text-[var(--foreground)] outline-none placeholder:text-[var(--muted)] focus:border-[var(--accent)]"
              />
              <div className="mt-3 flex justify-end">
                <button
                  type="button"
                  onClick={handleAddComment}
                  disabled={isAddingComment || !comment.trim()}
                  className="rounded-full bg-[var(--foreground)] px-4 py-2 text-sm font-semibold text-[var(--background)] transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {isAddingComment ? "Posting..." : "Post"}
                </button>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
