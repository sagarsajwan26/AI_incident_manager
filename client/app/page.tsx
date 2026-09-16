"use client";
import Link from "next/link";

import { useMeQuery } from "./lib/services/api";

export default function Home() {
  const { data: user, isLoading, isError } = useMeQuery();

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100"><div className="animate-pulse flex items-center space-x-2"><div className="w-4 h-4 bg-blue-600 dark:bg-blue-500 rounded-full"></div><div className="text-gray-500 dark:text-gray-400">Checking auth...</div></div></div>;
  if (isError) {
    // The user is not authenticated, we render the landing page.
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-50 dark:from-blue-900/20 via-white dark:via-gray-950 to-white dark:to-gray-950 text-gray-900 dark:text-gray-100 flex items-center justify-center px-6">
      {/* Animated glowing background elements */}
      <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 dark:opacity-10 animate-blob"></div>
      <div className="absolute top-0 -right-4 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 dark:opacity-10 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 dark:opacity-10 animate-blob animation-delay-4000"></div>

      <section className="relative z-10 w-full max-w-4xl text-center">
        <div>
          <div className="inline-flex items-center rounded-full border border-gray-200/50 dark:border-gray-800/50 bg-white/50 dark:bg-gray-900/50 backdrop-blur-md px-5 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 mb-8 shadow-sm">
            ✨ AI-Powered Incident Management
          </div>

          <h1 className="text-5xl font-extrabold tracking-tight sm:text-7xl mb-6">
            Investigate incidents
            <span className="block mt-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
              with intelligence.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg sm:text-xl leading-relaxed text-gray-600 dark:text-gray-400">
            Track production incidents, collect evidence, investigate root causes,
            and preserve investigation history in one{" "}
            <span className="text-gray-900 dark:text-gray-100 font-medium">unified platform</span>.
          </p>

          {user && !isError && (
            <div className="mt-8 mb-4 p-6 rounded-2xl border border-white/20 dark:border-white/10 bg-white/60 dark:bg-gray-900/60 backdrop-blur-xl inline-block text-left shadow-xl">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Welcome back, {user?.name}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mt-1">{user?.email}</p>
            </div>
          )}

          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6">
            {(!user || isError) && (
              <>
                <Link
                  href="/login"
                  className="w-full sm:w-auto rounded-full bg-blue-600 dark:bg-blue-500 px-8 py-3.5 font-medium text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/25 hover:-translate-y-0.5 active:scale-95"
                >
                  Sign In
                </Link>

                <Link
                  href="/signup"
                  className="w-full sm:w-auto rounded-full border border-gray-200 dark:border-gray-800 bg-white/50 dark:bg-gray-950/50 backdrop-blur-sm px-8 py-3.5 font-medium text-gray-900 dark:text-gray-100 transition-all hover:bg-gray-50 dark:hover:bg-gray-900 hover:shadow-md hover:-translate-y-0.5 active:scale-95"
                >
                  Create Account
                </Link>
              </>
            )}
            {user && !isError && (
              <Link
                href="/dashboard"
                className="w-full sm:w-auto rounded-full bg-blue-600 dark:bg-blue-500 px-8 py-3.5 font-medium text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-500/25 hover:-translate-y-0.5 active:scale-95"
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
