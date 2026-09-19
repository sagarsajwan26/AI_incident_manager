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
      const detail = error?.data?.detail;
      let msg = "Failed to connect integration. Please check your token.";
      if (typeof detail === "string") {
        msg = detail;
      } else if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
        msg = detail[0].msg;
      }
      setErrorMsg(msg);
    }
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl glass-panel p-6 shadow-xl animate-fade-in-up">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-black dark:text-white">Add Integration</h2>

            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Connect GitHub or Slack to your incident manager.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-gray-500 transition hover:bg-black/5 dark:hover:bg-white/10 dark:text-gray-400"
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
              className="mb-2 block text-sm font-medium text-black dark:text-gray-300"
            >
              Provider
            </label>

            <select
              id="provider"
              value={provider}
              onChange={(event) =>
                setProvider(event.target.value as IntegrationProvider)
              }
              className="w-full rounded-xl border border-transparent bg-black/5 dark:bg-white/5 px-4 py-3 text-sm text-black dark:text-white outline-none transition focus:border-gray-300 dark:focus:border-gray-700"
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
              className="w-full rounded-xl border border-transparent bg-black/5 dark:bg-white/5 px-4 py-3 text-sm text-black dark:text-white placeholder:text-gray-400 outline-none transition focus:border-gray-300 dark:focus:border-gray-700"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="rounded-full border border-gray-200/50 dark:border-white/10 bg-transparent px-4 py-2.5 text-sm font-semibold text-gray-500 dark:text-gray-300 transition hover:bg-black/5 dark:hover:bg-white/10 hover:text-black dark:hover:text-white disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="rounded-full bg-black px-6 py-2.5 text-sm font-semibold text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
            >
              {isLoading ? "Connecting..." : "Connect"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
