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
  tags: string[];
}

export interface InsightCard {
  problem: string;
  method: string;
  key_results: string[];
  limitations: string[];
  contributions: string[];
}

export interface Figure {
  id: string;
  page: number;
  caption: string;
}

export interface PaperDetail extends PaperSummary {
  abstract: string;
  metadata: { doi: string; year: string; venue: string; keywords: string[] };
  statistics: Record<string, number | string>;
  section_titles: string[];
  insight_card: InsightCard | null;
  insight_status: "pending" | "ready" | "unavailable";
  figures: Figure[];
}

export type ReadingLevel = "default" | "eli5" | "expert";

export interface Source {
  rank: number;
  section_title: string;
  page_start: number;
  page_end: number;
  score: number;
  preview: string;
  paper_title?: string;
}

export interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  sources: Source[];
  /** Ephemeral: suggested follow-ups shown right after an answer streams
   * in. Not persisted server-side, so these disappear on reload. */
  followups?: string[];
}

export type ExportFormat = "markdown" | "pdf";

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

/** Base path shared by single-paper chat (`/api/papers/{id}`) and
 * multi-paper compare (`/api/compare/{id1,id2,...}`) - both expose the
 * same chat/history/export/stream shape underneath. */
export function paperChatBase(id: string): string {
  return `/api/papers/${id}`;
}

export function compareChatBase(ids: string[]): string {
  return `/api/compare/${ids.join(",")}`;
}

export interface StreamHandlers {
  onSources: (sources: Source[]) => void;
  onDelta: (text: string) => void;
  onFollowups: (followups: string[]) => void;
  onDone: () => void;
  onError: (message: string) => void;
}

/** Reads a POST SSE-style stream (can't use EventSource - that's GET-only). */
export async function streamChat(
  basePath: string,
  question: string,
  topK: number,
  readingLevel: ReadingLevel,
  handlers: StreamHandlers
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${basePath}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: topK, reading_level: readingLevel }),
    });
  } catch {
    handlers.onError("Could not reach the backend.");
    return;
  }

  if (!res.ok || !res.body) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    handlers.onError(detail);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sepIndex: number;
    while ((sepIndex = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, sepIndex);
      buffer = buffer.slice(sepIndex + 2);

      const eventMatch = rawEvent.match(/^event: (.+)$/m);
      const dataMatch = rawEvent.match(/^data: (.+)$/m);
      if (!eventMatch || !dataMatch) continue;

      const event = eventMatch[1];
      const data = JSON.parse(dataMatch[1]);

      if (event === "sources") handlers.onSources(data);
      else if (event === "delta") handlers.onDelta(data.text);
      else if (event === "followups") handlers.onFollowups(data);
      else if (event === "done") handlers.onDone();
      else if (event === "error") handlers.onError(data.detail);
    }
  }
}

export function exportUrl(basePath: string, format: ExportFormat): string {
  return `${API_BASE}${basePath}/chat/export?format=${format}`;
}

export interface LibrarySearchResult {
  paper_id: string;
  paper_title: string;
  section_title: string;
  page_start: number;
  page_end: number;
  score: number;
  preview: string;
}

export interface RelatedPaper {
  title: string;
  abstract: string;
  year: number | null;
  authors: string[];
  url: string;
}

export function figureImageUrl(paperId: string, figureId: string): string {
  return `${API_BASE}/api/papers/${paperId}/figures/${figureId}`;
}

export const api = {
  uploadPaper: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<PaperSummary>("/api/papers/upload", { method: "POST", body: form });
  },
  importArxiv: (arxiv_id: string) =>
    request<PaperSummary>("/api/papers/import-arxiv", { method: "POST", body: JSON.stringify({ arxiv_id }) }),
  listPapers: () => request<PaperSummary[]>("/api/papers"),
  searchLibrary: (query: string) => request<LibrarySearchResult[]>(`/api/papers/search?q=${encodeURIComponent(query)}`),
  getPaper: (id: string) => request<PaperDetail>(`/api/papers/${id}`),
  getRelatedPapers: (id: string) => request<RelatedPaper[]>(`/api/papers/${id}/related`),
  askAboutFigure: (paperId: string, figureId: string, question: string) =>
    request<{ answer: string }>(`/api/papers/${paperId}/figures/${figureId}/ask`, {
      method: "POST",
      body: JSON.stringify({ question }),
    }),
  renamePaper: (id: string, title: string) =>
    request<PaperSummary>(`/api/papers/${id}`, { method: "PATCH", body: JSON.stringify({ title }) }),
  deletePaper: (id: string) => request<void>(`/api/papers/${id}`, { method: "DELETE" }),

  chat: (basePath: string, question: string, top_k = 5) =>
    request<{ answer: string; sources: Source[] }>(`${basePath}/chat`, {
      method: "POST",
      body: JSON.stringify({ question, top_k }),
    }),
  getChatHistory: (basePath: string) => request<ChatTurn[]>(`${basePath}/chat/history`),
  clearChatHistory: (basePath: string) => request<void>(`${basePath}/chat`, { method: "DELETE" }),
};

export { ApiError };
