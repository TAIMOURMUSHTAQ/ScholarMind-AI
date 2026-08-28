import { useEffect, useRef, useState } from "react";
import { api, ApiError, type ChatTurn } from "../api/client";

interface Props {
  paperId: string;
}

export default function ChatPanel({ paperId }: Props) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api
      .getChatHistory(paperId)
      .then(setTurns)
      .catch(() => undefined)
      .finally(() => setHistoryLoaded(true));
  }, [paperId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, sending]);

  const send = async () => {
    const question = input.trim();
    if (!question || sending) return;

    setInput("");
    setError(null);
    setTurns((prev) => [...prev, { role: "user", content: question, sources: [] }]);
    setSending(true);

    try {
      const result = await api.chat(paperId, question);
      setTurns((prev) => [...prev, { role: "assistant", content: result.answer, sources: result.sources }]);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.status === 429
            ? "Gemini's free-tier rate limit was hit. Please wait a minute and try again."
            : err.message
          : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-100 px-5 py-4">
        <h2 className="font-semibold text-slate-900">Chat with this paper</h2>
        <p className="text-xs text-slate-500">Answers are grounded in the paper's text, not general knowledge.</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-5 py-4">
        {!historyLoaded ? (
          <div className="flex h-full items-center justify-center text-sm text-slate-400">Loading conversation…</div>
        ) : turns.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-slate-400">
            <span className="text-3xl">💬</span>
            <p className="text-sm">
              Ask something like <span className="italic">"What is the main contribution?"</span>
            </p>
          </div>
        ) : (
          turns.map((turn, i) => <ChatBubble key={i} turn={turn} />)
        )}

        {sending && (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span className="flex gap-1">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300" />
            </span>
            thinking…
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="mx-5 mb-2 rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{error}</p>}

      <div className="flex items-end gap-2 border-t border-slate-100 p-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          rows={1}
          placeholder="Ask a follow-up question…"
          className="max-h-32 flex-1 resize-none rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
        />
        <button
          onClick={send}
          disabled={sending || !input.trim()}
          className="rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          Send
        </button>
      </div>
    </div>
  );
}

function ChatBubble({ turn }: { turn: ChatTurn }) {
  const isUser = turn.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] ${isUser ? "" : "w-full"}`}>
        <div
          className={`whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${
            isUser ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-800"
          }`}
        >
          {turn.content}
        </div>
        {!isUser && turn.sources.length > 0 && (
          <div className="mt-2 space-y-1.5">
            {turn.sources.map((source) => (
              <details key={source.rank} className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs">
                <summary className="cursor-pointer select-none font-medium text-slate-600">
                  Source {source.rank} - {source.section_title} (p.{source.page_start}-{source.page_end}) ·{" "}
                  {Math.round(source.score * 100)}% match
                </summary>
                <p className="mt-1.5 text-slate-500">{source.preview}…</p>
              </details>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
