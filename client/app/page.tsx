"use client";
import Link from "next/link";
import { useMeQuery } from "./lib/services/api";

export default function Home() {
  const { data: user, isLoading, isError } = useMeQuery();

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-black text-[#1d1d1f] dark:text-[#f5f5f7]">
      <div className="animate-pulse flex items-center space-x-2">
        <div className="text-gray-500 dark:text-gray-400 font-medium">Checking auth...</div>
      </div>
    </div>
  );

  return (
    <main className="relative min-h-screen bg-white dark:bg-black text-[#1d1d1f] dark:text-[#f5f5f7] flex items-center justify-center px-6 overflow-hidden">
      <section className="relative z-10 w-full max-w-4xl text-center">
        <div className="animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-7xl mb-4 text-black dark:text-white">
            Investigate incidents.
            <br />
            <span className="text-gray-400 dark:text-gray-500">With intelligence.</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg sm:text-2xl leading-relaxed text-gray-500 dark:text-gray-400 font-medium">
            Track production incidents, collect evidence, investigate root causes,
            and preserve investigation history in one unified platform.
          </p>

          {user && !isError && (
            <div className="mt-10 mb-4 p-6 rounded-2xl glass-panel inline-block text-left shadow-sm border border-gray-100 dark:border-gray-800">
              <h2 className="text-xl font-bold text-black dark:text-white">
                Welcome back, {user?.name}
              </h2>
              <p className="text-gray-500 dark:text-gray-400 mt-1">{user?.email}</p>
            </div>
          )}

          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4">
            {(!user || isError) && (
              <>
                <Link
                  href="/login"
                  className="w-full sm:w-auto rounded-full bg-black dark:bg-white text-white dark:text-black px-8 py-3.5 font-semibold transition-all hover:scale-105 active:scale-95 shadow-sm"
                >
                  Sign In
                </Link>

                <Link
                  href="/signup"
                  className="w-full sm:w-auto rounded-full bg-gray-100 dark:bg-gray-900 text-black dark:text-white px-8 py-3.5 font-semibold transition-all hover:bg-gray-200 dark:hover:bg-gray-800 hover:scale-105 active:scale-95"
                >
                  Create Account
                </Link>
              </>
            )}
            {user && !isError && (
              <Link
                href="/dashboard"
                className="w-full sm:w-auto rounded-full bg-black dark:bg-white text-white dark:text-black px-8 py-3.5 font-semibold transition-all hover:scale-105 active:scale-95 shadow-sm"
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
