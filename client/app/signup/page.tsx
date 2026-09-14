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
    <main className="min-h-screen flex items-center justify-center bg-[var(--background)] px-4 py-12 text-[var(--foreground)]">
      <section className="w-full max-w-md">
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--background)] p-8 shadow-sm">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="mb-4 inline-flex rounded-full border border-[var(--border)] bg-[var(--background)] px-3 py-1 text-xs font-medium text-[var(--muted)]">
              AI Incident Manager
            </div>

            <h1 className="text-4xl font-extrabold tracking-tight text-[var(--foreground)]">
              Create an Account
            </h1>

            <p className="mt-2 text-sm text-[var(--muted)]">
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
                className="mb-2 block text-sm font-medium text-[var(--foreground)]"
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
                className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {/* Name */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="firstName"
                  className="mb-2 block text-sm font-medium text-[var(--foreground)]"
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
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>

              <div>
                <label
                  htmlFor="lastName"
                  className="mb-2 block text-sm font-medium text-[var(--foreground)]"
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
                  className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted)] focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] disabled:cursor-not-allowed disabled:opacity-60"
                />
              </div>
            </div>

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
                autoComplete="new-password"
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
              {isLoading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          {/* Login */}
          <p className="mt-8 text-center text-sm text-[var(--muted)]">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-[var(--accent)] transition hover:opacity-80"
            >
              Sign in
            </Link>
          </p>
        </div>
      </section>
    </main>
  );
}
