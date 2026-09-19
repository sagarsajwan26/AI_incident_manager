"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRegisterMutation } from "../lib/services/api";

export default function SignupPage() {
  const [tenantName, setTenantName] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [register, { isLoading }] = useRegisterMutation();

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setSuccessMessage("");
    setErrorMessage("");

    const name = `${firstName} ${lastName}`.trim();

    try {
      await register({
        tenant_name: tenantName.trim(),
        name,
        email: email.trim(),
        password,
      }).unwrap();

      setSuccessMessage("Account created successfully.");

      setTenantName("");
      setFirstName("");
      setLastName("");
      setEmail("");
      setPassword("");
    } catch (error: unknown) {
      const apiError = error as {
        data?: {
          detail?: string;
        };
      };

      const detail = apiError?.data?.detail;
      let errorMsg = "Unable to create your account. Please try again.";
      if (typeof detail === "string") {
        errorMsg = detail;
      } else if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
        errorMsg = detail[0].msg;
      }

      setErrorMessage(errorMsg);
    }
  }

  return (
    <main className="relative min-h-screen bg-gray-50 dark:bg-black px-4 py-12 flex items-center justify-center overflow-hidden">
      <section className="relative z-10 w-full max-w-md animate-fade-in-up">
        <div className="rounded-2xl glass-panel p-8 shadow-sm border border-gray-200/50 dark:border-gray-800/50">
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-black dark:text-white">
              Create an Account
            </h1>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Create your workspace and start managing incidents.
            </p>
          </div>

          {/* Success */}
          {successMessage && (
            <div
              role="status"
              className="mb-6 rounded-lg border border-green-500/20 bg-green-50 px-4 py-3 text-sm text-green-700 dark:bg-green-900/30 dark:text-green-400"
            >
              {successMessage}
            </div>
          )}

          {/* Error */}
          {errorMessage && (
            <div
              role="alert"
              className="mb-6 rounded-lg border border-red-500/20 bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-900/30 dark:text-red-400"
            >
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Tenant */}
            <div>
              <label
                htmlFor="tenantName"
                className="mb-2 block text-sm font-medium text-black dark:text-white"
              >
                Organization Name
              </label>
              <input
                id="tenantName"
                name="tenantName"
                type="text"
                value={tenantName}
                onChange={(event) => setTenantName(event.target.value)}
                placeholder="Acme Inc."
                autoComplete="organization"
                required
                disabled={isLoading}
                className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Name */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="firstName"
                  className="mb-2 block text-sm font-medium text-black dark:text-white"
                >
                  First Name
                </label>
                <input
                  id="firstName"
                  name="firstName"
                  type="text"
                  value={firstName}
                  onChange={(event) => setFirstName(event.target.value)}
                  placeholder="John"
                  autoComplete="given-name"
                  required
                  disabled={isLoading}
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>

              <div>
                <label
                  htmlFor="lastName"
                  className="mb-2 block text-sm font-medium text-black dark:text-white"
                >
                  Last Name
                </label>
                <input
                  id="lastName"
                  name="lastName"
                  type="text"
                  value={lastName}
                  onChange={(event) => setLastName(event.target.value)}
                  placeholder="Doe"
                  autoComplete="family-name"
                  required
                  disabled={isLoading}
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-black dark:text-white"
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
                className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-black dark:text-white"
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
                autoComplete="new-password"
                minLength={8}
                required
                disabled={isLoading}
                className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-black/50 px-4 py-3 text-black dark:text-white outline-none transition placeholder:text-gray-400 focus:border-gray-400 dark:focus:border-gray-600 focus:ring-1 focus:ring-gray-400 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-full bg-black dark:bg-white px-4 py-3 font-semibold text-white dark:text-black shadow-sm transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          {/* Login */}
          <p className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-black dark:text-white transition hover:opacity-70"
            >
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
