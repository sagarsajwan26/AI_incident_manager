"use client";
import {
  type IntegrationProvider,
  useCreateIntegrationMutation,
} from "@/app/lib/services/api";

import { XMarkIcon } from "@heroicons/react/24/outline";
import { useState } from "react";

type ConnectIntegrationProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function ConnectIntegrationmodel({
  isOpen,
  onClose,
}: ConnectIntegrationProps) {
  const [provider, setProvider] = useState<IntegrationProvider>("github");
  const [token, setToken] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [createIntegration, { isLoading }] = useCreateIntegrationMutation();
  if (!isOpen) {
    return null;
  }

  const handleClose = () => {
    setErrorMsg("");
    setToken("");
    setProvider("github");
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      await createIntegration({
        provider,
        credentials: {
          token,
        },
        is_active: true,
      }).unwrap();

      handleClose();
    } catch (error: any) {
      console.error("Failed to create integration:", error);
      setErrorMsg(
        error?.data?.detail || "Failed to connect integration. Please check your token."
      );
    }
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-gray-900 p-6 shadow-2xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white">Add Integration</h2>

            <p className="mt-1 text-sm text-gray-400">
              Connect GitHub or Slack to your incident manager.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-gray-400 transition hover:bg-white/10 hover:text-white"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {errorMsg && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm font-medium text-red-500">
              {errorMsg}
            </div>
          )}

          <div>
            <label
              htmlFor="provider"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Provider
            </label>

            <select
              id="provider"
              value={provider}
              onChange={(event) =>
                setProvider(event.target.value as IntegrationProvider)
              }
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none transition focus:border-blue-500"
            >
              <option value="github" className="bg-gray-900">
                GitHub
              </option>

              <option value="slack" className="bg-gray-900">
                Slack
              </option>
            </select>
          </div>

          <div>
            <label
              htmlFor="token"
              className="mb-2 block text-sm font-medium text-gray-300"
            >
              Access Token
            </label>

            <input
              id="token"
              type="password"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="Enter your access token"
              required
              className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder:text-gray-500 outline-none transition focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-semibold text-gray-300 transition hover:bg-white/10 hover:text-white disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Connecting..." : "Connect"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
