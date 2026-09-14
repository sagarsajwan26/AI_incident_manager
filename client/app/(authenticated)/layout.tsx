"use client";

import AuthGuard from "../components/auth/AuthGuard";
import AppShell from "../components/auth/layout/AppShell";
export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <AppShell>{children}</AppShell>
    </AuthGuard>
  );
}
