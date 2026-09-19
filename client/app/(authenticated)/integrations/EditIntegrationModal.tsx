"use client";

import {
  useGetIntegrationQuery,
  useUpdateIntegrationMutation,
} from "@/app/lib/services/api";
import { XMarkIcon } from "@heroicons/react/24/outline";
import { useEffect, useState } from "react";

type EditIntegrationModalProps = {
  integrationId: number | null;
  isOpen: boolean;
  onClose: () => void;
};

export default function EditIntegrationModal({
  integrationId,
  isOpen,
  onClose,
}: EditIntegrationModalProps) {
  const shouldFetch = isOpen && integrationId !== null;
  const {
    data: integration,
    isLoading: isLoadingIntegration,
    isError: isFetchError,
  } = useGetIntegrationQuery(integrationId as number, {
    skip: !shouldFetch,
  });
  const [updateIntegration, { isLoading: isUpdating }] =
    useUpdateIntegrationMutation();
  const [token, setToken] = useState("");
  const [isActive, setIsActive] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    if (!integration) {
      return;
    }

    setIsActive(integration.is_active);
    setToken("");
    setErrorMsg("");
    setSuccessMsg("");
  });
  if (!isOpen || integrationId === null) {
    return null;
  }
  const handleClose = () => {
    setToken("");
    setErrorMsg("");
    setSuccessMsg("");
    onClose();
  };
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const body: {
        integrationId: number;
        credentials?: {
          token: string;
        };
        is_Active: boolean;
      } = {
        integrationId,
        is_Active: isActive,
      };

      if (token.trim()) {
        body.credentials = {
          token: token.trim(),
        };
      }

      await updateIntegration(body).unwrap();
      setSuccessMsg("integration updated successfully");
      setTimeout(() => {
        handleClose();
      }, 800);
    } catch (error: any) {
      console.error("Failed to update integration:", error);
      const detail = error?.data?.detail;
      let message = "Failed to update integration.";
      if (typeof detail === "string") {
        message = detail;
      } else if (Array.isArray(detail) && detail.length > 0 && detail[0]?.msg) {
        message = detail[0].msg;
      }
      setErrorMsg(message);
    }
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm">
      {" "}
      <div className="w-full max-w-md animate-fade-in-up rounded-2xl glass-panel p-6 shadow-xl">
        {" "}
        {/* Header */}{" "}
        <div className="mb-6 flex items-center justify-between">
          {" "}
          <div>
            {" "}
            <h2 className="text-xl font-bold text-black dark:text-white">
              {" "}
              Edit Integration{" "}
            </h2>{" "}
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {" "}
              Update your {integration?.provider ?? "integration"}{" "}
              settings.{" "}
            </p>{" "}
          </div>{" "}
          <button
            type="button"
            onClick={handleClose}
            disabled={isUpdating}
            className="rounded-full p-2 text-gray-500 transition hover:bg-black/5 hover:text-black disabled:cursor-not-allowed disabled:opacity-50 dark:text-gray-400 dark:hover:bg-white/10 dark:hover:text-white"
          >
            {" "}
            <XMarkIcon className="h-5 w-5" />{" "}
          </button>{" "}
        </div>{" "}
        {/* Loading */}{" "}
        {isLoadingIntegration ? (
          <div className="flex min-h-[180px] items-center justify-center">
            {" "}
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200/50 border-t-gray-900 dark:border-white/20 dark:border-t-white" />{" "}
          </div>
        ) : isFetchError || !integration ? (
          /* Fetch Error */ <div className="space-y-4">
            {" "}
            <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm font-medium text-red-500 dark:text-red-400">
              {" "}
              Failed to load integration details.{" "}
            </div>{" "}
            <div className="flex justify-end">
              {" "}
              <button
                type="button"
                onClick={handleClose}
                className="rounded-full bg-black px-5 py-2.5 text-sm font-semibold text-white dark:bg-white dark:text-black"
              >
                {" "}
                Close{" "}
              </button>{" "}
            </div>{" "}
          </div>
        ) : (
          /* Form */ <form onSubmit={handleSubmit} className="space-y-5">
            {" "}
            {/* Error */}{" "}
            {errorMsg && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm font-medium text-red-500 dark:text-red-400">
                {" "}
                {errorMsg}{" "}
              </div>
            )}{" "}
            {/* Success */}{" "}
            {successMsg && (
              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm font-medium text-emerald-600 dark:text-emerald-400">
                {" "}
                {successMsg}{" "}
              </div>
            )}{" "}
            {/* Provider */}{" "}
            <div>
              {" "}
              <label className="mb-2 block text-sm font-medium text-black dark:text-gray-300">
                {" "}
                Provider{" "}
              </label>{" "}
              <div className="rounded-xl bg-black/5 px-4 py-3 text-sm font-medium capitalize text-black dark:bg-white/5 dark:text-white">
                {" "}
                {integration.provider}{" "}
              </div>{" "}
            </div>{" "}
            {/* Token */}{" "}
            <div>
              {" "}
              <label
                htmlFor="edit-token"
                className="mb-2 block text-sm font-medium text-black dark:text-gray-300"
              >
                {" "}
                New Access Token{" "}
              </label>{" "}
              <input
                id="edit-token"
                type="password"
                value={token}
                onChange={(event) => setToken(event.target.value)}
                placeholder="Leave blank to keep current token"
                disabled={isUpdating}
                className="w-full rounded-xl border border-transparent bg-black/5 px-4 py-3 text-sm text-black outline-none transition placeholder:text-gray-400 focus:border-gray-300 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white/5 dark:text-white dark:focus:border-gray-700"
              />{" "}
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {" "}
                Enter a new token only if you want to replace the current
                token.{" "}
              </p>{" "}
            </div>{" "}
            {/* Active Toggle */}{" "}
            <label className="flex cursor-pointer items-center justify-between rounded-xl bg-black/5 px-4 py-3 dark:bg-white/5">
              {" "}
              <div>
                {" "}
                <p className="text-sm font-medium text-black dark:text-white">
                  {" "}
                  Active{" "}
                </p>{" "}
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {" "}
                  Allow this integration to be used for investigations.{" "}
                </p>{" "}
              </div>{" "}
              <input
                type="checkbox"
                checked={isActive}
                onChange={(event) => setIsActive(event.target.checked)}
                disabled={isUpdating}
                className="h-4 w-4"
              />{" "}
            </label>{" "}
            {/* Buttons */}{" "}
            <div className="flex justify-end gap-3 pt-2">
              {" "}
              <button
                type="button"
                onClick={handleClose}
                disabled={isUpdating}
                className="rounded-full border border-gray-200/50 bg-transparent px-4 py-2.5 text-sm font-semibold text-gray-500 transition hover:bg-black/5 hover:text-black disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:text-gray-300 dark:hover:bg-white/10 dark:hover:text-white"
              >
                {" "}
                Cancel{" "}
              </button>{" "}
              <button
                type="submit"
                disabled={isUpdating}
                className="rounded-full bg-black px-6 py-2.5 text-sm font-semibold text-white transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-white dark:text-black"
              >
                {" "}
                {isUpdating ? "Saving..." : "Save Changes"}{" "}
              </button>{" "}
            </div>{" "}
          </form>
        )}{" "}
      </div>{" "}
    </div>
  );
}
