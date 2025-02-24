"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // If logged in, go straight to /chat
    if (isAuthenticated) {
      router.push("/chat");
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex flex-col items-center justify-center h-[80vh] text-center gap-4">
      <h1 className="text-3xl font-bold">Welcome to TES</h1>
      <p className="text-gray-600">An AI Chat Application.</p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
        >
          Login
        </Link>
        <Link
          href="/register"
          className="px-4 py-2 border border-black rounded hover:bg-gray-100"
        >
          Register
        </Link>
      </div>
    </div>
  );
}
