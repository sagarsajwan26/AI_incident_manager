"use client";
import { useMeQuery } from "@/app/lib/services/api";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

type AuthGuardProps = {
  children: React.ReactNode;
};

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const { data: user, isLoading, isError } = useMeQuery();
  useEffect(() => {
    if (!isLoading && isError) {
      router.replace("/login");
    }
  }, [isLoading, isError, router]);

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gray-950 text-white">
        <p className="text-gray-400">Checking authentication...</p>
      </main>
    );
  }
  if (!user) return null;
  return <>{children}</>;
}
