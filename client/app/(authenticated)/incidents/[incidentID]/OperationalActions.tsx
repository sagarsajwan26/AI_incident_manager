"use client";

import { useState } from "react";
import {
  type IncidentActionPhase,
  useCreateIncidentActionMutation,
  useGetIncidentActionsQuery,
} from "@/app/lib/services/api";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";

type OperationalActionsProps = {
  incidentId: number;
  incidentStatus: string;
};

const phaseLabels: Record<IncidentActionPhase, string> = {
  containment: "Containment",
  resolution: "Resolution",
  closure: "Closure",
};

export default function OperationalActions({
  incidentId,
  incidentStatus,
}: OperationalActionsProps) {
  const {
    data: actions = [],
    isLoading,
    isError,
  } = useGetIncidentActionsQuery(incidentId);

  const [createIncidentAction, { isLoading: isCreating }] =
    useCreateIncidentActionMutation();

  const [phase, setPhase] = useState<IncidentActionPhase>("containment");

  const [actionType, setActionType] = useState("");
  const [description, setDescription] = useState("");
  const [outcome, setOutcome] = useState("");
  const [createError, setCreateError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!actionType.trim() || !description.trim()) {
      return;
    }

    try {
      setCreateError(null);
      await createIncidentAction({
        incidentId,
        phase,
        action_type: actionType.trim(),
        description: description.trim(),
        outcome: outcome.trim() || null,
      }).unwrap();

      setActionType("");
      setDescription("");
      setOutcome("");
    } catch (error) {
      setCreateError(
        getApiErrorMessage(
          error,
          "Failed to record the operational action.",
        ),
      );
    }
  };

  return (
    <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900">
          Operational Actions
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Record containment, resolution, and closure actions taken on this
          incident.
        </p>
      </div>

      {/* Create Action */}
      <form onSubmit={handleSubmit} className="mb-8 space-y-4">
        <div>
          <label
            htmlFor="action-phase"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Phase
          </label>

          <select
            id="action-phase"
            value={phase}
            onChange={(e) => setPhase(e.target.value as IncidentActionPhase)}
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="containment">Containment</option>

            <option value="resolution">Resolution</option>

            <option value="closure" disabled={incidentStatus !== "resolved"}>
              Closure
            </option>
          </select>
        </div>

        <div>
          <label
            htmlFor="action-type"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Action Type
          </label>

          <input
            id="action-type"
            type="text"
            value={actionType}
            onChange={(e) => setActionType(e.target.value)}
            placeholder="e.g. disable_service"
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label
            htmlFor="action-description"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Description
          </label>

          <textarea
            id="action-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe what was done..."
            rows={3}
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label
            htmlFor="action-outcome"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Outcome
          </label>

          <textarea
            id="action-outcome"
            value={outcome}
            onChange={(e) => setOutcome(e.target.value)}
            placeholder="What was the result?"
            rows={2}
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        {createError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-3">
            <p className="text-sm text-red-600">{createError}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isCreating || !actionType.trim() || !description.trim()}
          className="rounded-xl bg-black px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isCreating ? "Recording..." : "Record Action"}
        </button>
      </form>

      {/* Action History */}
      <div>
        <h3 className="mb-4 text-sm font-semibold text-gray-900">
          Action History
        </h3>

        {isLoading && (
          <p className="text-sm text-gray-500">
            Loading operational actions...
          </p>
        )}

        {isError && (
          <p className="text-sm text-red-600">
            Failed to load operational actions.
          </p>
        )}

        {!isLoading && !isError && actions.length === 0 && (
          <p className="text-sm text-gray-500">
            No operational actions have been recorded yet.
          </p>
        )}

        <div className="space-y-4">
          {actions.map((action) => (
            <article
              key={action.id}
              className="rounded-xl border border-gray-200 p-4"
            >
              <div className="flex items-center justify-between gap-4">
                <div>
                  <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
                    {phaseLabels[action.phase]}
                  </span>

                  <h4 className="mt-1 font-medium text-gray-900">
                    {action.action_type}
                  </h4>
                </div>

                <time
                  dateTime={action.created_at}
                  className="text-xs text-gray-500"
                >
                  {new Date(action.created_at).toLocaleString()}
                </time>
              </div>

              <p className="mt-3 text-sm text-gray-700">{action.description}</p>

              {action.outcome && (
                <div className="mt-3 rounded-lg bg-gray-50 p-3">
                  <p className="text-xs font-medium text-gray-500">Outcome</p>

                  <p className="mt-1 text-sm text-gray-700">{action.outcome}</p>
                </div>
              )}
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
