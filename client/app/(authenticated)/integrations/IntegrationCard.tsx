"use client";

import type { Integration } from "@/app/lib/services/api";
import { PencilIcon } from "@heroicons/react/24/outline";

type IntegrationCardProps = {
  integration: Integration;
  onTest: (integrationId: number) => void;
  isTesting?: boolean;
  onDelete: (integrationId: number) => void;
  isDeleting?: boolean;
  onEdit: (integrationId: number) => void;
};

export default function IntegrationCard({
  integration,
  onTest,
  isTesting = false,
  onDelete,
  isDeleting = false,
  onEdit,
}: IntegrationCardProps) {
  return (
    <div className="group relative overflow-hidden rounded-2xl glass-panel p-6 shadow-sm transition-transform hover:scale-[1.02]">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 opacity-0 transition-opacity group-hover:opacity-100" />

      <div className="relative">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-black/5 shadow-inner dark:bg-white/10">
              <span className="text-xl font-bold uppercase text-black dark:text-white">
                {integration.provider.charAt(0)}
              </span>
            </div>

            <div>
              <h2 className="text-lg font-bold capitalize text-black dark:text-white">
                {integration.provider}
              </h2>

              <p className="text-sm text-gray-500 dark:text-gray-400">
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

        <div className="mt-6 flex items-center justify-end gap-3 border-t border-gray-200/50 pt-4 dark:border-gray-800/50">
          <button
            type="button"
            onClick={() => onEdit(integration.id)}
            disabled={isDeleting || isTesting}
            className="inline-flex items-center gap-2 rounded-full border border-gray-300/50 bg-black/5 px-4 py-2 text-sm font-semibold text-gray-700 transition hover:bg-black/10 disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:bg-white/5 dark:text-gray-300 dark:hover:bg-white/10"
          >
            <PencilIcon className="h-4 w-4" />
            Edit
          </button>

          <button
            type="button"
            onClick={() => onDelete(integration.id)}
            disabled={isDeleting || isTesting}
            className="rounded-full border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-500 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-50 dark:text-red-400"
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </button>

          <button
            type="button"
            onClick={() => onTest(integration.id)}
            disabled={isTesting || isDeleting}
            className="rounded-full bg-black px-4 py-2 text-sm font-semibold text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
          >
            {isTesting ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white dark:border-black/20 dark:border-t-black" />
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
