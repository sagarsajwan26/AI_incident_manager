"use client";
import Link from "next/link";

import { useMeQuery } from "./lib/services/api";

export default function Home() {
  const { data: user, isLoading, isError } = useMeQuery();

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-[var(--background)] text-[var(--foreground)]"><div className="animate-pulse flex items-center space-x-2"><div className="w-4 h-4 bg-[var(--accent)] rounded-full"></div><div className="text-[var(--muted)]">Checking auth...</div></div></div>;
  if (isError) {
    // The user is not authenticated, we render the landing page.
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[var(--background)] text-[var(--foreground)] flex items-center justify-center px-6">
      <section className="relative z-10 w-full max-w-4xl text-center">
        <div>
          <div className="inline-flex items-center rounded-full border border-[var(--border)] bg-[var(--background)] px-5 py-2 text-sm font-medium text-[var(--muted)] mb-8 shadow-sm">
            ✨ AI-Powered Incident Management
          </div>

          <h1 className="text-5xl font-extrabold tracking-tight sm:text-7xl mb-6">
            Investigate incidents
            <span className="block mt-2 text-[var(--foreground)]">
              with intelligence.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg sm:text-xl leading-relaxed text-[var(--muted)]">
            Track production incidents, collect evidence, investigate root causes,
            and preserve investigation history in one{" "}
            <span className="text-[var(--foreground)] font-medium">unified platform</span>.
          </p>

          {user && !isError && (
            <div className="mt-8 mb-4 p-6 rounded-2xl border border-[var(--border)] bg-[var(--background)] inline-block text-left shadow-sm">
              <h2 className="text-2xl font-bold text-[var(--foreground)]">
                Welcome back, {user?.name}
              </h2>
              <p className="text-[var(--muted)] mt-1">{user?.email}</p>
            </div>
          )}

          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6">
            {(!user || isError) && (
              <>
                <Link
                  href="/login"
                  className="w-full sm:w-auto rounded-full bg-[var(--accent)] px-8 py-3.5 font-medium text-white transition-all hover:opacity-90 active:scale-[0.98]"
                >
                  Sign In
                </Link>

                <Link
                  href="/signup"
                  className="w-full sm:w-auto rounded-full border border-[var(--border)] bg-transparent px-8 py-3.5 font-medium text-[var(--foreground)] transition-all hover:bg-black/5 dark:hover:bg-white/5 active:scale-[0.98]"
                >
                  Create Account
                </Link>
              </>
            )}
            {user && !isError && (
              <Link
                href="/dashboard"
                className="w-full sm:w-auto rounded-full bg-[var(--accent)] px-8 py-3.5 font-medium text-white transition-all hover:opacity-90 active:scale-[0.98]"
              >
                Go to Dashboard
              </Link>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
