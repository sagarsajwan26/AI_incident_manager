"use client";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useLoginMutation } from "../lib/services/api";
import { useState } from "react";
import { FormEvent } from "react";
export default function Login() {
  const [login, { isLoading }] = useLoginMutation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const router = useRouter();
  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSuccessMessage("");
    setErrorMessage("");
    try {
      await login({
        email: email.trim(),
        password: password.trim(),
      }).unwrap();

      router.replace("/dashboard");

      setSuccessMessage("login success");
      setEmail("");
      setPassword("");
    } catch (error) {
      const apiError = error as {
        data?: {
          detail?: string;
        };
      };

      setErrorMessage(
        apiError?.data?.detail ||
          "Unable to create your account. Please try again.",
      );
    }
  }
  return (
    <main className="min-h-screen flex items-center justify-center bg-[var(--background)] px-4 py-12 text-[var(--foreground)]">
      <section className="w-full max-w-md">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-8 shadow-sm">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex rounded-full border border-[var(--border)] bg-[var(--background)] px-3 py-1 text-xs font-medium text-[var(--muted)]">
              AI Incident Manager
            </div>

            <h1 className="text-4xl font-extrabold tracking-tight text-[var(--foreground)]">
              Welcome Back
            </h1>

            <p className="mt-2 text-sm text-[var(--muted)]">
              Sign in to your workspace to continue.
            </p>
          </div>

          {/* Success */}
          {successMessage && (
            <div
              role="status"
              className="mb-6 rounded-lg border border-green-500/20 bg-green-50 px-4 py-3 text-sm text-green-700 dark:bg-green-500/10 dark:text-green-300"
            >
              {successMessage}
            </div>
          )}

          {/* Error */}
          {error && (
            <div
              role="alert"
              className="mb-6 rounded-lg border border-red-500/20 bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-300"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-[var(--foreground)]"
              >
                Email Address
              </label>

              <input
                id="email"
                name="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
                disabled={isLoading}
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-[var(--foreground)]"
              >
                Password
              </label>

              <input
                id="password"
                name="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                minLength={8}
                required
                disabled={isLoading}
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-lg bg-[var(--accent)] px-4 py-3 font-semibold text-white shadow-sm transition hover:opacity-90 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Login */}
          <p className="mt-8 text-center text-sm text-[var(--muted)]">
            Don't have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-[var(--accent)] transition hover:opacity-80"
            >
              Sign up
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
