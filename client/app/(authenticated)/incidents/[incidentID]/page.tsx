"use client";

import { useParams } from "next/navigation";
import Link from "next/link";

import {
  useGetIncidentQuery,
  useInvestigateIncidentMutation,
  useUpdateIncidentStatusMutation,
  type Incident,
} from "@/app/lib/services/api";
import IncidentHeader from "./components/IncidentHeader";
import CommentsSection from "./components/CommentSection";
import EvidenceSection from "./components/EvidenceSection";
import { InvestigationHistory } from "./components/InvestigationHistory";
import AuditTimeline from "./components/AuditTimeline";
import GithubEvidenceCollector from "./GithubEvidenceCollector";
import OperationalActions from "./OperationalActions";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";
export default function IncidentDetailPage() {
  const params = useParams();
  const incidentId = Number(params.incidentID);

  const {
    data: incident,
    isLoading,
    isError,
  } = useGetIncidentQuery(incidentId, {
    skip: !Number.isInteger(incidentId),
  });

  const [
    investigateIncident,
    { isLoading: isInvestigating, isError: isInvestigationError },
  ] = useInvestigateIncidentMutation();

  const handleInvestigate = async () => {
    try {
      await investigateIncident(incidentId).unwrap();
    } catch (error) {
      console.error("Investigation failed:", error);
    }
  };

  const [
    updateIncidentStatus,
    { isLoading: isUpdatingStatus, isError: isStatusError, error: statusError },
  ] = useUpdateIncidentStatusMutation();

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
        <p className="text-gray-500 dark:text-gray-400">Loading incident...</p>
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
      <IncidentHeader
        incident={incident}
        isInvestigating={isInvestigating}
        isUpdatingStatus={isUpdatingStatus}
        onInvestigate={handleInvestigate}
        onStatusChange={handleStatusChange}
      />
      <nav>
        <Link
          href="/incidents"
          className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
        >
          ← Back to incidents
        </Link>
      </nav>

      {/* GitHub Evidence Collector - Top of page */}
      <GithubEvidenceCollector incidentId={incidentId} />

      {isInvestigationError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-500/20 dark:bg-red-500/10">
          <p className="text-sm font-medium text-red-600 dark:text-red-400">
            Investigation failed. Please try again.
          </p>
        </div>
      )}

      {isStatusError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-500/20 dark:bg-red-500/10">
          <p className="text-sm font-medium text-red-600 dark:text-red-400">
            {getApiErrorMessage(
              statusError,
              "Failed to update incident status. Please try again.",
            )}
          </p>
        </div>
      )}
      {/* Incident Header & Overview */}

      {/* Incident Metadata */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 animate-fade-in-up">
        <article className="rounded-2xl glass-panel p-5 shadow-sm transition-transform hover:-translate-y-1 hover:scale-[1.02]">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400">
            Reported by
          </h3>
          <p className="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">
            User #{incident.reported_by}
          </p>
        </article>

        <article className="rounded-2xl glass-panel p-5 shadow-sm transition-transform hover:-translate-y-1 hover:scale-[1.02]">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400">
            Assigned to
          </h3>
          <p className="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">
            {incident.assigned_to
              ? `User #${incident.assigned_to}`
              : "Unassigned"}
          </p>
        </article>

        <article className="rounded-2xl glass-panel p-5 shadow-sm transition-transform hover:-translate-y-1 hover:scale-[1.02]">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400">
            Created
          </h3>
          <p className="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">
            {new Date(incident.created_at).toLocaleString()}
          </p>
        </article>

        <article className="rounded-2xl glass-panel p-5 shadow-sm transition-transform hover:-translate-y-1 hover:scale-[1.02]">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400">
            Last updated
          </h3>
          <p className="mt-1 text-sm font-medium text-gray-900 dark:text-gray-100">
            {new Date(incident.updated_at).toLocaleString()}
          </p>
        </article>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Evidence Column */}
        <div className="space-y-6">
          <EvidenceSection incidentId={incidentId} />
        </div>

        {/* History and Comments Column */}
        <InvestigationHistory incidentId={incidentId} />
      </div>
      <CommentsSection incidentId={incidentId} />
      <AuditTimeline incidentId={incidentId} />
      <OperationalActions
        incidentId={incident.id}
        incidentStatus={incident.status}
      />
    </main>
  );
}
