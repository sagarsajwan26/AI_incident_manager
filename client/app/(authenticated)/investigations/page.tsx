import React from "react";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";

export default function InvestigationsPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <div className="flex max-w-md flex-col items-center justify-center rounded-3xl border border-white/10 bg-white/5 p-12 text-center shadow-2xl backdrop-blur-xl">
        <div className="mb-6 rounded-full bg-blue-500/10 p-5">
          <MagnifyingGlassIcon className="h-10 w-10 text-blue-400" />
        </div>
        <h1 className="mb-2 text-2xl font-bold tracking-tight text-white">
          Investigations
        </h1>
        <p className="text-sm leading-relaxed text-gray-400">
          This page is under construction. Future updates will display all ongoing and historical investigations across your incidents here.
        </p>
      </div>
    </div>
  );
}
