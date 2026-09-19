import type { Integration } from "@/app/lib/services/api";
import {
  useDeleteIntegrationMutation,
  useTestIntegrationMutation,
} from "@/app/lib/services/api";
import { useState } from "react";

type IntegrationCardProps = {
  integration: Integration;
  onTest: (integrationId: number) => void;
  isTesting?: boolean;
  onDelete: (integrationId: number) => void;
  isDeleting?: boolean;
};

export default function IntegrationCard({
  integration,
  onTest,
  isTesting = false,
  onDelete,
  isDeleting = false,
}: IntegrationCardProps) {
  useTestIntegrationMutation();

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl transition-all hover:bg-white/10 hover:shadow-2xl hover:shadow-blue-500/10">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 opacity-0 transition-opacity group-hover:opacity-100" />

      <div className="relative">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10 shadow-inner">
              <span className="text-xl font-bold uppercase text-white">
                {integration.provider.charAt(0)}
              </span>
            </div>

            <div>
              <h2 className="text-lg font-bold capitalize text-white">
                {integration.provider}
              </h2>

              <p className="text-sm text-gray-400">
                {integration.is_active ? "Active Connection" : "Inactive Setup"}
              </p>
            </div>
          </div>

          <span
            className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold backdrop-blur-md ${
              integration.is_active
                ? "border border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
                : "border border-gray-500/20 bg-gray-500/10 text-gray-400"
            }`}
          >
            {integration.is_active ? (
              <>
                <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400" />
                Connected
              </>
            ) : (
              <>
                <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-gray-400" />
                Inactive
              </>
            )}
          </span>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3 border-t border-white/5 pt-4">
          <button
            type="button"
            onClick={() => onDelete(integration.id)}
            disabled={isDeleting}
            className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-400 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </button>

          <button
            type="button"
            onClick={() => onTest(integration.id)}
            disabled={isTesting}
            className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white shadow-sm backdrop-blur-md transition-all hover:bg-white/10 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isTesting ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white" />
                Testing...
              </span>
            ) : (
              "Test Connection"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
