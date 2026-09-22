import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";

type ApiErrorResponse = {
  detail?: string | Array<{ msg?: string }>;
};

export function getApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again.",
): string {
  if (!error || typeof error !== "object") {
    return fallback;
  }

  if (!("status" in error) || !("data" in error)) {
    return fallback;
  }

  const apiError = error as FetchBaseQueryError;

  if (!apiError.data || typeof apiError.data !== "object") {
    return fallback;
  }

  const data = apiError.data as ApiErrorResponse;

  if (typeof data.detail === "string") {
    return data.detail;
  }

  if (Array.isArray(data.detail)) {
    const messages = data.detail
      .map((item) => item.msg)
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join(", ");
    }
  }

  return fallback;
}
