"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Incidents", href: "/incidents" },
  { label: "Investigations", href: "/investigations" },
  { label: "Integrations", href: "/integrations" },
];

export const Sidebar = () => {
  const pathname = usePathname();
  
  return (
    <aside className="h-full glass-panel flex flex-col p-4 w-64 shadow-[1px_0_0_0_rgba(0,0,0,0.05)] dark:shadow-[1px_0_0_0_rgba(255,255,255,0.05)] z-20">
      <div className="mb-10 px-2">
        <h1 className="text-lg font-semibold text-black dark:text-white">
          AI Incident Manager
        </h1>
        <p className="mt-1 text-xs font-medium text-gray-400 dark:text-gray-500 uppercase tracking-wider">
          Operations
        </p>
      </div>

      <nav className="space-y-1 flex-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-4 py-2.5 text-sm font-medium transition-colors duration-200 ${
                isActive
                  ? "bg-black/5 dark:bg-white/10 text-black dark:text-white"
                  : "text-gray-500 dark:text-gray-400 hover:bg-black/5 dark:hover:bg-white/5 hover:text-black dark:hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto px-2">
        <div className="rounded-xl border border-gray-100 dark:border-gray-800 bg-white/50 dark:bg-black/50 p-4 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2 font-medium">Need help?</p>
          <button className="w-full text-xs py-2 rounded-lg bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 text-black dark:text-white font-medium transition-all hover:bg-gray-100 dark:hover:bg-gray-800">
            Documentation
          </button>
        </div>
      </div>
    </aside>
  );
};
