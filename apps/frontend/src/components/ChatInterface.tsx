"use client";

import React, { useEffect, useState, FormEvent } from "react";
import { getChatMessagesApi, sendChatMessageApi } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ChatInterfaceProps {
  sessionId: number | null;
}

export default function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    if (sessionId) {
      fetchMessages();
    }
  }, [sessionId]);

  async function fetchMessages() {
    if (!sessionId) return;
    try {
      const data = await getChatMessagesApi(sessionId);
      setMessages(data);
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault();
    if (!sessionId || !input.trim()) return;

    // Optimistic update
    const userMsg: ChatMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const assistantRes = await sendChatMessageApi(sessionId, input);
      if (assistantRes.assistant_response) {
        const assistantMsg: ChatMessage = {
          role: "assistant",
          content: assistantRes.assistant_response,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (err) {
      console.error("Send chat message error:", err);
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`mb-2 ${m.role === "user" ? "text-right" : "text-left"}`}
          >
            <div
              className={`inline-block px-3 py-2 rounded ${
                m.role === "user"
                  ? "bg-black text-white"
                  : "bg-gray-200 text-black"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Input Box */}
      <form onSubmit={handleSend} className="p-4 border-t border-gray-300 flex">
        <input
          className="flex-1 border border-gray-400 rounded px-3 py-2 mr-2"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800"
        >
          Send
        </button>
      </form>
    </div>
  );
}
