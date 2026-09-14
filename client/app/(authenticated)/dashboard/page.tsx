"use client";

export default function DashboardPage() {
  return (
    <main className="relative min-h-screen bg-[var(--background)] px-8 py-12 text-[var(--foreground)]">
      <div className="relative z-10">
        <div className="inline-flex items-center rounded-full border border-[var(--border)] bg-[var(--background)] px-4 py-1.5 text-xs font-semibold text-[var(--muted)] mb-6 shadow-sm uppercase tracking-wider">
          Overview
        </div>
        
        <h1 className="text-4xl font-extrabold tracking-tight text-[var(--foreground)]">
          AI Incident Manager Dashboard
        </h1>

        <div className="mt-8 p-6 rounded-2xl border border-[var(--border)] bg-[var(--background)] shadow-sm inline-block">
          <p className="text-[var(--foreground)] flex items-center gap-3 text-lg">
            <span className="flex h-3 w-3 rounded-full bg-green-500 shadow-sm"></span>
            You are successfully authenticated.
          </p>
        </div>
      </div>
    </main>
  );
}
