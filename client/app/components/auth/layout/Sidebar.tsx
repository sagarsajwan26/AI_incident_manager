"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
const navigation = [
  {
    label: "Dashboard",
    href: "/dashboard",
  },
  {
    label: "Incidents",
    href: "/incidents",
  },
  {
    label: "Investigations",
    href: "/investigations",
  },
  {
    label: "Integrations",
    href: "/integrations",
  },
];
export const Sidebar = () => {
  const pathname = usePathname();
  return (
    <aside className="h-full bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 flex flex-col p-4 w-64 shadow-sm z-20">
      <div className="mb-10 px-2">
        <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          AI Incident Manager
        </h1>

        <p className="mt-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Operations Platform
        </p>
      </div>
      <nav className="space-y-1 flex-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? "bg-black/5 dark:bg-white/10 text-gray-900 dark:text-gray-100"
                  : "text-gray-500 dark:text-gray-400 hover:bg-black/5 dark:hover:bg-white/5 hover:text-gray-900 dark:text-gray-100"
              }`}
            >
              <span className="relative z-10">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto px-2">
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-black/5 dark:bg-white/5 p-4 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Need help?</p>
          <button className="w-full text-xs py-2 rounded-lg bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 text-gray-900 dark:text-gray-100 font-medium transition-colors hover:bg-black/5 dark:hover:bg-white/10 shadow-sm">
            Documentation
          </button>
        </div>
      </div>
    </aside>
  );
};
