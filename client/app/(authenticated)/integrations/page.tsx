"use client";

import ConnectIntegrationmodel from "./ConnectIntegrationModel";
import {
  useGetIntegrationsQuery,
  useTestIntegrationMutation,
  useDeleteIntegrationMutation,
} from "@/app/lib/services/api";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";
import IntegrationCard from "./IntegrationCard";
import {
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { useState } from "react";
import EditIntegrationModal from "./EditIntegrationModal";

export default function IntegrationPage() {
  const [editingIntegrationId, setEditingIntegrationId] = useState<
    number | null
  >(null);
  const { data: integrations, isLoading, isError } = useGetIntegrationsQuery();

  const [testIntegration] = useTestIntegrationMutation();
  const [deleteIntegration] = useDeleteIntegrationMutation();

  const [testResult, setTestResult] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  const [testingIntegrationId, setTestingIntegrationId] = useState<
    number | null
  >(null);

  const [deletingIntegrationId, setDeletingIntegrationId] = useState<
    number | null
  >(null);

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleTest = async (integrationId: number) => {
    try {
      setTestResult(null);
      setTestingIntegrationId(integrationId);

      await testIntegration(integrationId).unwrap();

      setTestResult({
        type: "success",
        message: "Connection test successful!",
      });

      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      setTestResult({
        type: "error",
        message: getApiErrorMessage(
          error,
          "Connection test failed. Please check credentials.",
        ),
      });

      setTimeout(() => setTestResult(null), 5000);
    } finally {
      setTestingIntegrationId(null);
    }
  };

  const handleDelete = async (integrationId: number) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this integration?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setDeletingIntegrationId(integrationId);

      await deleteIntegration(integrationId).unwrap();
    } catch (error) {
      setTestResult({
        type: "error",
        message: getApiErrorMessage(error, "Failed to delete integration."),
      });
      setTimeout(() => setTestResult(null), 5000);
    } finally {
      setDeletingIntegrationId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center animate-fade-in-up">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200/50 border-t-gray-900 dark:border-white/20 dark:border-t-white"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 animate-fade-in-up">
        <div className="rounded-2xl glass-panel border border-red-500/20 p-6 shadow-sm">
          <p className="text-sm font-medium text-red-500 dark:text-red-400">
            Failed to load integrations. Please try again.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen p-8">
      {testResult && (
        <div className="fixed left-1/2 top-8 z-50 -translate-x-1/2 animate-in fade-in slide-in-from-top-4">
          <div
            className={`flex items-center gap-3 rounded-full border px-6 py-3 shadow-lg glass-panel ${
              testResult.type === "success"
                ? "border-emerald-500/30 text-emerald-600 dark:text-emerald-400"
                : "border-red-500/30 text-red-600 dark:text-red-400"
            }`}
          >
            {testResult.type === "success" ? (
              <CheckCircleIcon className="h-5 w-5" />
            ) : (
              <XCircleIcon className="h-5 w-5" />
            )}

            <span className="text-sm font-semibold">{testResult.message}</span>
          </div>
        </div>
      )}

      <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in-up">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-black dark:text-white">
            Integrations
          </h1>

          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Connect external services to enrich your AI incident investigations.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          className="inline-flex justify-center items-center gap-2 rounded-full bg-black dark:bg-white px-5 py-2.5 text-sm font-semibold text-white dark:text-black shadow-sm transition-transform hover:scale-[1.02] active:scale-[0.98]"
        >
          <PlusIcon className="h-5 w-5" />
          Add Integration
        </button>
      </div>

      {integrations && integrations.length === 0 ? (
        <button
          type="button"
          onClick={() => setIsModalOpen(true)}
          className="flex min-h-[300px] w-full flex-col items-center justify-center rounded-3xl glass-panel p-12 text-center shadow-sm transition-transform hover:scale-[1.01] animate-fade-in-up"
        >
          <div className="mb-4 rounded-full bg-black/5 dark:bg-white/5 p-4">
            <PlusIcon className="h-8 w-8 text-gray-400" />
          </div>

          <h3 className="text-lg font-semibold text-black dark:text-white">
            No integrations found
          </h3>

          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Get started by connecting a new service.
          </p>
        </button>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {integrations?.map((integration) => (
            <IntegrationCard
              key={integration.id}
              integration={integration}
              onTest={handleTest}
              isTesting={testingIntegrationId === integration.id}
              onDelete={handleDelete}
              isDeleting={deletingIntegrationId === integration.id}
              onEdit={(integrationId) => setEditingIntegrationId(integrationId)}
            />
          ))}
        </div>
      )}

      <ConnectIntegrationmodel
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
      <EditIntegrationModal
        integrationId={editingIntegrationId}
        isOpen={editingIntegrationId !== null}
        onClose={() => setEditingIntegrationId(null)}
      />
    </div>
  );
}
