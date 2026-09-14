"use client";
import React from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-[var(--background)] text-[var(--foreground)] overflow-hidden">
      <div className="z-20">
        <Sidebar />
      </div>

      <div className="flex-1 flex flex-col relative overflow-hidden">
        <div className="z-10 relative">
          <Topbar />
        </div>

        <main className="flex-1 overflow-y-auto p-6 z-10 relative custom-scrollbar">
          {children}
        </main>
      </div>
    </div>
  );
}
