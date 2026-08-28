const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface PaperSummary {
  id: string;
  filename: string;
  title: string;
  authors: string[];
  upload_time: string;
  status: "processing" | "ready" | "failed";
  error_message: string | null;
  num_pages: number;
  num_chunks: number;
}

export interface PaperDetail extends PaperSummary {
  abstract: string;
  metadata: { doi: string; year: string; venue: string; keywords: string[] };
  statistics: Record<string, number | string>;
  section_titles: string[];
}

export interface Source {
  rank: number;
  section_title: string;
  page_start: number;
  page_end: number;
  score: number;
  preview: string;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  sources: Source[];
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options?.body && !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  uploadPaper: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<PaperSummary>("/api/papers/upload", { method: "POST", body: form });
  },
  listPapers: () => request<PaperSummary[]>("/api/papers"),
  getPaper: (id: string) => request<PaperDetail>(`/api/papers/${id}`),
  deletePaper: (id: string) => request<void>(`/api/papers/${id}`, { method: "DELETE" }),
  chat: (id: string, question: string, top_k = 5) =>
    request<{ answer: string; sources: Source[] }>(`/api/papers/${id}/chat`, {
      method: "POST",
      body: JSON.stringify({ question, top_k }),
    }),
  getChatHistory: (id: string) => request<ChatTurn[]>(`/api/papers/${id}/chat/history`),
  clearChatHistory: (id: string) => request<void>(`/api/papers/${id}/chat`, { method: "DELETE" }),
};

export { ApiError };
