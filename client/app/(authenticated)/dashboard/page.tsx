"use client";

export default function DashboardPage() {
  return (
    <main className="relative min-h-screen bg-white dark:bg-gray-950 px-8 py-12 text-gray-900 dark:text-gray-100">
      <div className="relative z-10">
        <div className="inline-flex items-center rounded-full border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-1.5 text-xs font-semibold text-gray-500 dark:text-gray-400 mb-6 shadow-sm uppercase tracking-wider">
          Overview
        </div>
        
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100">
          AI Incident Manager Dashboard
        </h1>

        <div className="mt-8 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shadow-sm inline-block">
          <p className="text-gray-900 dark:text-gray-100 flex items-center gap-3 text-lg">
            <span className="flex h-3 w-3 rounded-full bg-green-500 shadow-sm"></span>
            You are successfully authenticated.
          </p>
        </div>
      </div>
    </main>
  );
}
