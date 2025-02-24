"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import ChatInterface from "@/components/ChatInterface";
import FileUploadForm from "@/components/FileUploadForm";

export default function ChatPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(
    null
  );

  useEffect(() => {
    // If not logged in, redirect to login
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  return (
    <div className="flex h-[calc(100vh-3rem)]">
      {/* Left sidebar for sessions, user info, etc. */}
      <Sidebar
        selectedSessionId={selectedSessionId}
        onSelectSession={(id) => setSelectedSessionId(id)}
      />

      {/* Main content area */}
      <div className="flex-1 flex flex-col bg-[#f7f7f8]">
        {/* Chat messages & input form */}
        <div className="flex-1 overflow-auto">
          <ChatInterface sessionId={selectedSessionId} />
        </div>

        {/* File upload at bottom */}
        <div className="border-t border-gray-300 p-4">
          <FileUploadForm />
        </div>
      </div>
    </div>
  );
}
