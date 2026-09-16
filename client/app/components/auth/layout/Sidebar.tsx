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
    <aside className="h-full bg-white/80 dark:bg-gray-950/80 backdrop-blur-xl border-r border-gray-200/50 dark:border-gray-800/50 flex flex-col p-4 w-64 shadow-xl z-20">
      <div className="mb-10 px-2">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
          AI Incident Manager
        </h1>

        <p className="mt-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Operations Platform
        </p>
      </div>
      <nav className="space-y-2 flex-1">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-xl px-4 py-3 text-sm font-medium transition-all ${
                isActive
                  ? "bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 shadow-sm border border-blue-100 dark:border-blue-800/50"
                  : "text-gray-500 dark:text-gray-400 border border-transparent hover:bg-gray-50 dark:hover:bg-white/5 hover:text-gray-900 dark:text-gray-100 hover:border-gray-200/50 dark:hover:border-white/10"
              }`}
            >
              <span className="relative z-10 flex items-center">
                {isActive && (
                  <span className="absolute -left-2 w-1 h-5 bg-blue-600 dark:bg-blue-500 rounded-full" />
                )}
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto px-2">
        <div className="rounded-2xl border border-gray-200/50 dark:border-gray-800/50 bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 p-5 text-center shadow-sm">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 font-medium">Need help?</p>
          <button className="w-full text-xs py-2.5 rounded-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-900 dark:text-gray-100 font-medium transition-all hover:shadow-md hover:-translate-y-0.5 active:scale-95">
            Documentation
          </button>
        </div>
      </div>
    </aside>
  );
};
