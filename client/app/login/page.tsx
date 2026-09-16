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
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-50 dark:from-blue-900/20 via-white dark:via-gray-950 to-white dark:to-gray-950 px-4 py-12 flex items-center justify-center">
      {/* Animated glowing background elements */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 dark:opacity-10 animate-blob"></div>
      <div className="absolute top-0 -right-4 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 dark:opacity-10 animate-blob animation-delay-2000"></div>

      <section className="relative z-10 w-full max-w-md">
        <div className="rounded-2xl border border-white/20 dark:border-white/10 bg-white/60 dark:bg-gray-900/60 backdrop-blur-xl p-8 shadow-xl">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex rounded-full border border-gray-200/50 dark:border-gray-800/50 bg-white/50 dark:bg-gray-950/50 backdrop-blur-md px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400">
              AI Incident Manager
            </div>

            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100">
              Welcome Back
            </h1>

            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
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
                className="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100"
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
                className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3 text-gray-900 dark:text-gray-100 outline-none transition placeholder:text-gray-500 dark:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100"
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
                className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3 text-gray-900 dark:text-gray-100 outline-none transition placeholder:text-gray-500 dark:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-xl bg-blue-600 dark:bg-blue-500 px-4 py-3 font-semibold text-white shadow-lg shadow-blue-500/25 transition-all hover:bg-blue-700 hover:-translate-y-0.5 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          {/* Login */}
          <p className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
            Don't have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-blue-600 dark:text-blue-400 transition hover:opacity-80"
            >
              Sign up
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
