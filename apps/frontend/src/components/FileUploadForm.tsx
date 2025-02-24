"use client";

import React, { useState, FormEvent } from "react";
import { uploadDocumentApi } from "@/lib/api";

export default function FileUploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    try {
      const res = await uploadDocumentApi(file);
      setMessage(`File uploaded: Document ID ${res.document_id}`);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setMessage(`Error uploading file: ${err.message}`);
      } else {
        console.error("An unknown error occurred", err);
      }
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button
          type="submit"
          className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800"
        >
          Upload
        </button>
      </form>
      {message && <p className="mt-2 text-sm text-gray-600">{message}</p>}
    </div>
  );
}
