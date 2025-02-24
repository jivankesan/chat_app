"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "./AuthProvider";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const { isAuthenticated, token } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    router.refresh();
  };

  return (
    <nav className="bg-black text-white h-12 flex items-center px-4 justify-between">
      <div className="font-bold text-lg">My ChatGPT App</div>
      <div className="space-x-4">
        {isAuthenticated ? (
          <>
            <span className="text-sm text-gray-300">Logged in</span>
            <button
              onClick={handleLogout}
              className="text-sm underline hover:text-gray-200"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="underline text-sm hover:text-gray-200"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="underline text-sm hover:text-gray-200"
            >
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
