"use client";

import {
  useGetIntegrationsQuery,
  useTestIntegrationMutation,
} from "@/app/lib/services/api";
import IntegrationCard from "./IntegrationCard";
import { PlusIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";
import { useState } from "react";

export default function IntegrationPage() {
  const { data: integrations, isLoading, isError } = useGetIntegrationsQuery();
  const [testIntegration, { isLoading: isTesting }] = useTestIntegrationMutation();
  const [testResult, setTestResult] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const handleTest = async (integrationId: number) => {
    try {
      setTestResult(null);
      await testIntegration(integrationId).unwrap();
      setTestResult({ type: 'success', message: 'Connection test successful!' });
      setTimeout(() => setTestResult(null), 3000);
    } catch (error) {
      console.error("Integration test failed:", error);
      setTestResult({ type: 'error', message: 'Connection test failed. Please check credentials.' });
      setTimeout(() => setTestResult(null), 5000);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-white/20 border-t-white"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8">
        <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-6 backdrop-blur-xl">
          <p className="text-sm font-medium text-red-400">Failed to load integrations. Please try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 relative">
      {/* Toast Notification */}
      {testResult && (
        <div className="fixed top-8 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-4">
          <div className={`flex items-center gap-3 rounded-full px-6 py-3 shadow-2xl backdrop-blur-xl border ${
            testResult.type === 'success' 
              ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400' 
              : 'bg-red-500/20 border-red-500/30 text-red-400'
          }`}>
            {testResult.type === 'success' ? (
              <CheckCircleIcon className="h-5 w-5" />
            ) : (
              <XCircleIcon className="h-5 w-5" />
            )}
            <span className="text-sm font-semibold">{testResult.message}</span>
          </div>
        </div>
      )}

      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Integrations</h1>
          <p className="mt-2 text-sm text-gray-400">
            Connect external services to enrich your AI incident investigations.
          </p>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg transition-all hover:bg-blue-500 hover:shadow-blue-500/25 active:scale-95"
        >
          <PlusIcon className="h-5 w-5" />
          Add Integration
        </button>
      </div>

      {integrations && integrations.length === 0 ? (
        <div className="flex min-h-[300px] flex-col items-center justify-center rounded-3xl border border-white/5 bg-white/5 p-12 text-center backdrop-blur-xl">
          <div className="mb-4 rounded-full bg-white/5 p-4">
            <PlusIcon className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-white">No integrations found</h3>
          <p className="mt-2 text-sm text-gray-400">Get started by connecting a new service.</p>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {integrations?.map((integration) => (
            <IntegrationCard
              key={integration.id}
              integration={integration}
              onTest={handleTest}
              isTesting={isTesting}
            />
          ))}
        </div>
      )}
    </div>
  );
}
