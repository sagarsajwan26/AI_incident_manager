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
              className="mb-6 rounded-lg border border-green-500/20 bg-green-50 px-4 py-3 text-sm text-green-700 dark:bg-green-500/10 dark:text-green-300"
            >
              {successMessage}
            </div>
          )}

          {/* Error */}
          {errorMessage && (
            <div
              role="alert"
              className="mb-6 rounded-lg border border-red-500/20 bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-500/10 dark:text-red-300"
            >
              {errorMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Tenant */}
            <div>
              <label
                htmlFor="tenantName"
                className="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100"
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
                className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3 text-gray-900 dark:text-gray-100 outline-none transition placeholder:text-gray-500 dark:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Name */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="firstName"
                  className="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100"
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
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3 text-gray-900 dark:text-gray-100 outline-none transition placeholder:text-gray-500 dark:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>

              <div>
                <label
                  htmlFor="lastName"
                  className="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100"
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
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3 text-gray-900 dark:text-gray-100 outline-none transition placeholder:text-gray-500 dark:text-gray-400 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>
            </div>

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
                autoComplete="new-password"
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
              {isLoading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          {/* Login */}
          <p className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-blue-600 dark:text-blue-400 transition hover:opacity-80"
            >
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
