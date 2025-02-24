export const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken() {
  return typeof window !== "undefined"
    ? localStorage.getItem("access_token")
    : null;
}

function authHeaders() {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
}

// 1) Register
export async function registerUserApi(email: string, password: string) {
  const res = await fetch(`${BASE_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

// 2) Login
export async function loginUserApi(email: string, password: string) {
  // FastAPI expects x-www-form-urlencoded for OAuth2PasswordRequestForm
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  const data = await res.json();
  return data.access_token;
}

// 3) Get user chats
export async function getUserChatsApi() {
  const res = await fetch(`${BASE_URL}/chats`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

// 4) Create chat session
export async function createChatSessionApi(sessionName: string) {
  const res = await fetch(`${BASE_URL}/start_chat`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ session_name: sessionName }),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

// 5) Get chat messages
export async function getChatMessagesApi(sessionId: number) {
  const res = await fetch(`${BASE_URL}/chat_messages/${sessionId}`, {
    headers: authHeaders(),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

// 6) Send chat message
export async function sendChatMessageApi(sessionId: number, message: string) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

// 7) Upload document
export async function uploadDocumentApi(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers: {
      Authorization: authHeaders().Authorization || "",
    },
    body: formData,
  });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}