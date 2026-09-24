"use client";
import { Incident, useCreateIncidentMutation } from "@/app/lib/services/api";
import React, { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import { getApiErrorMessage } from "@/app/lib/utils/apiError";

export default function CreateIncidentPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<Incident["severity"]>("medium");
  const [provider, setProvider] = useState("");
  const [resourceType, setResourceType] = useState("");
  const [identifier, setIdentifier] = useState("");
  const [includeResource, setIncludeResource] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const router = useRouter();
  const [createIncident, { isLoading }] = useCreateIncidentMutation();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setErrorMsg(null);
      const incident = await createIncident({
        title: title.trim(),
        description: description.trim(),
        severity,
        ...(includeResource && provider.trim() && resourceType.trim() && identifier.trim()
          ? {
              resource: {
                provider: provider.trim(),
                resource_type: resourceType.trim(),
                identifier: identifier.trim(),
              },
            }
          : {}),
      }).unwrap();

      router.push(`/incidents/${incident.id}`);
    } catch (error) {
      setErrorMsg(getApiErrorMessage(error));
    }
  };

  return (
    <main className="mx-auto max-w-2xl p-8 animate-fade-in-up">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-black dark:text-white">
          Create Incident
        </h1>

        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          Report a production incident for investigation.
        </p>
      </div>

      {errorMsg && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-600">{errorMsg}</p>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-6 rounded-2xl glass-panel p-8 shadow-sm"
      >
        {/* Title */}
        <div>
          <label
            htmlFor="title"
            className="mb-2 block text-sm font-semibold text-black dark:text-white"
          >
            Title
          </label>

          <input
            id="title"
            name="title"
            type="text"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="API requests failing in production"
            required
            disabled={isLoading}
            className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-sm text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>

        {/* Description */}
        <div>
          <label
            htmlFor="description"
            className="mb-2 block text-sm font-semibold text-black dark:text-white"
          >
            Description
          </label>

          <textarea
            id="description"
            name="description"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Describe what happened, when it started, and what users are experiencing..."
            rows={6}
            required
            disabled={isLoading}
            className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-sm text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>

        {/* Severity */}
        <div>
          <label
            htmlFor="severity"
            className="mb-2 block text-sm font-semibold text-black dark:text-white"
          >
            Severity
          </label>

          <div className="relative">
            <select
              id="severity"
              name="severity"
              value={severity}
              onChange={(event) =>
                setSeverity(event.target.value as Incident["severity"])
              }
              disabled={isLoading}
              className="w-full appearance-none rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-sm text-black dark:text-white outline-none transition focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Associated Resource (Optional) */}
        <div className="pt-4 border-t border-gray-200/50 dark:border-gray-800/50">
          <label className="flex items-center gap-3 cursor-pointer mb-4">
            <input
              type="checkbox"
              checked={includeResource}
              onChange={(e) => setIncludeResource(e.target.checked)}
              disabled={isLoading}
              className="h-4 w-4 rounded border-gray-300 dark:border-gray-700 text-black dark:text-white focus:ring-black dark:focus:ring-white bg-white/50 dark:bg-black/50"
            />
            <span className="text-sm font-semibold text-black dark:text-white">
              Link an Associated Resource (Optional)
            </span>
          </label>

          {includeResource && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-fade-in-up">
              <div>
                <label
                  htmlFor="provider"
                  className="mb-2 block text-sm font-semibold text-gray-700 dark:text-gray-300"
                >
                  Provider
                </label>
                <input
                  id="provider"
                  type="text"
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  placeholder="e.g. aws, github"
                  required={includeResource}
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-sm text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <div>
                <label
                  htmlFor="resourceType"
                  className="mb-2 block text-sm font-semibold text-gray-700 dark:text-gray-300"
                >
                  Resource Type
                </label>
                <input
                  id="resourceType"
                  type="text"
                  value={resourceType}
                  onChange={(e) => setResourceType(e.target.value)}
                  placeholder="e.g. ec2_instance, repo"
                  required={includeResource}
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-sm text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <div>
                <label
                  htmlFor="identifier"
                  className="mb-2 block text-sm font-semibold text-gray-700 dark:text-gray-300"
                >
                  Identifier
                </label>
                <input
                  id="identifier"
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="e.g. i-1234567890abcdef0"
                  required={includeResource}
                  disabled={isLoading}
                  className="w-full rounded-xl border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-sm text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 border-t border-gray-200/50 dark:border-gray-800/50 pt-6">
          <button
            type="button"
            onClick={() => router.back()}
            disabled={isLoading}
            className="rounded-full px-4 py-2.5 text-sm font-semibold text-gray-500 transition hover:text-black dark:hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={
              isLoading ||
              !title.trim() ||
              !description.trim() ||
              (includeResource && (!provider.trim() || !resourceType.trim() || !identifier.trim()))
            }
            className="inline-flex items-center gap-2 rounded-full bg-black dark:bg-white px-6 py-2.5 text-sm font-semibold text-white dark:text-black shadow-sm transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white dark:border-black/20 dark:border-t-black" />
                Creating...
              </>
            ) : (
              <>
                <ExclamationTriangleIcon className="h-5 w-5" />
                Create Incident
              </>
            )}
          </button>
        </div>
      </form>
    </main>
  );
}
