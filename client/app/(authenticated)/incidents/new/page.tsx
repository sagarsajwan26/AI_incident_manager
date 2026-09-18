"use client";
import { Incident, useCreateIncidentMutation } from "@/app/lib/services/api";
import React, { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

export default function CreateIncidentPage() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState<Incident["severity"]>("medium");
  const router = useRouter();
  const [createIncident, { isLoading }] = useCreateIncidentMutation();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const incident = await createIncident({
        title: title.trim(),
        description: description.trim(),
        severity,
      }).unwrap();

      router.push(`/incidents/${incident.id}`);
    } catch (error) {
      console.error("Failed to create incident:", error);
    }
  };

  return (
    <main className="mx-auto max-w-2xl p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Create Incident
        </h1>

        <p className="mt-2 text-sm text-gray-400">
          Report a production incident for investigation.
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-6 rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl"
      >
        {/* Title */}
        <div>
          <label
            htmlFor="title"
            className="mb-2 block text-sm font-semibold text-gray-300"
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
            className="w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>

        {/* Description */}
        <div>
          <label
            htmlFor="description"
            className="mb-2 block text-sm font-semibold text-gray-300"
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
            className="w-full rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition placeholder:text-gray-600 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-50"
          />
        </div>

        {/* Severity */}
        <div>
          <label
            htmlFor="severity"
            className="mb-2 block text-sm font-semibold text-gray-300"
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
              className="w-full appearance-none rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="low" className="bg-gray-900 text-white">Low</option>
              <option value="medium" className="bg-gray-900 text-white">Medium</option>
              <option value="high" className="bg-gray-900 text-white">High</option>
              <option value="critical" className="bg-gray-900 text-white">Critical</option>
            </select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 border-t border-white/10 pt-6">
          <button
            type="button"
            onClick={() => router.back()}
            disabled={isLoading}
            className="rounded-xl px-4 py-2.5 text-sm font-semibold text-gray-300 transition hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={isLoading || !title.trim() || !description.trim()}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg transition-all hover:bg-blue-500 hover:shadow-blue-500/25 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/20 border-t-white" />
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
