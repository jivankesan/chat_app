"use client";

import React, { useEffect, useState } from "react";
import { useAuth } from "./AuthProvider";
import { getUserChatsApi, createChatSessionApi } from "@/lib/api";

interface ChatSession {
  session_id: number;
  session_name: string;
  created_at: string;
}

interface SidebarProps {
  selectedSessionId: number | null;
  onSelectSession: (id: number) => void;
}

export default function Sidebar({
  selectedSessionId,
  onSelectSession,
}: SidebarProps) {
  const { isAuthenticated } = useAuth();
  const [chats, setChats] = useState<ChatSession[]>([]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchChats();
    }
  }, [isAuthenticated]);

  async function fetchChats() {
    try {
      const data = await getUserChatsApi();
      setChats(data);
    } catch (err) {
      console.error("Error fetching chats:", err);
    }
  }

  async function handleNewChat() {
    try {
      const { session_id } = await createChatSessionApi("New Chat");
      await fetchChats();
      onSelectSession(session_id);
    } catch (err) {
      console.error("Error creating new chat:", err);
    }
  }

  return (
    <div className="bg-black text-white w-64 p-4 flex flex-col">
      <button
        onClick={handleNewChat}
        className="bg-gray-800 py-2 px-4 rounded mb-4 hover:bg-gray-700"
      >
        + New Chat
      </button>

      <div className="flex-1 overflow-y-auto">
        {chats.map((chat) => (
          <div
            key={chat.session_id}
            onClick={() => onSelectSession(chat.session_id)}
            className={`p-2 cursor-pointer rounded mb-2 ${
              selectedSessionId === chat.session_id
                ? "bg-gray-700"
                : "hover:bg-gray-800"
            }`}
          >
            <div className="font-semibold text-sm">
              {chat.session_name || `Session ${chat.session_id}`}
            </div>
            <div className="text-xs text-gray-400">
              {new Date(chat.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
