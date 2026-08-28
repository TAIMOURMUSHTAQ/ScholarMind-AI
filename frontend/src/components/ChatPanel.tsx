import { useEffect, useRef, useState } from "react";
import { api, exportUrl, streamChat, type ChatTurn, type ExportFormat } from "../api/client";

interface Props {
  basePath: string;
  title?: string;
  subtitle?: string;
}

export default function ChatPanel({
  basePath,
  title = "Chat with this paper",
  subtitle = "Answers are grounded in the paper's text, not general knowledge.",
}: Props) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setHistoryLoaded(false);
    api
      .getChatHistory(basePath)
      .then(setTurns)
      .catch(() => setTurns([]))
      .finally(() => setHistoryLoaded(true));
  }, [basePath]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, sending]);

  const send = async () => {
    const question = input.trim();
    if (!question || sending) return;

    setInput("");
    setError(null);
    setTurns((prev) => [...prev, { role: "user", content: question, sources: [] }, { role: "assistant", content: "", sources: [] }]);
    setSending(true);

    await streamChat(basePath, question, 5, {
      onSources: (sources) => {
        setTurns((prev) => {
          const next = [...prev];
          next[next.length - 1] = { ...next[next.length - 1], sources };
          return next;
        });
      },
      onDelta: (text) => {
        setTurns((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          next[next.length - 1] = { ...last, content: last.content + text };
          return next;
        });
      },
      onDone: () => setSending(false),
      onError: (message) => {
        setSending(false);
        setTurns((prev) => prev.slice(0, -1));
        setError(
          message.toLowerCase().includes("rate limit")
            ? "Gemini's free-tier rate limit was hit. Please wait a minute and try again."
            : message
        );
      },
    });
  };

  const handleExport = (format: ExportFormat) => {
    setExportOpen(false);
    window.open(exportUrl(basePath, format), "_blank");
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-start justify-between gap-3 border-b border-slate-100 px-5 py-4">
        <div>
          <h2 className="font-semibold text-slate-900">{title}</h2>
          <p className="text-xs text-slate-500">{subtitle}</p>
        </div>
        <div className="relative shrink-0">
          <button
            onClick={() => setExportOpen((v) => !v)}
            disabled={turns.length === 0}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Export ▾
          </button>
          {exportOpen && (
            <div className="absolute right-0 z-10 mt-1 w-40 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg">
              <button
                onClick={() => handleExport("markdown")}
                className="block w-full px-3 py-2 text-left text-xs text-slate-700 hover:bg-slate-50"
              >
                Markdown (.md)
              </button>
              <button
                onClick={() => handleExport("pdf")}
                className="block w-full px-3 py-2 text-left text-xs text-slate-700 hover:bg-slate-50"
              >
                PDF (.pdf)
              </button>
            </div>
          )}
        </div>
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
          turns.map((turn, i) => <ChatBubble key={i} turn={turn} pending={sending && i === turns.length - 1 && turn.role === "assistant"} />)
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

function ChatBubble({ turn, pending }: { turn: ChatTurn; pending: boolean }) {
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
          {pending && !turn.content && (
            <span className="flex gap-1 py-0.5">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
            </span>
          )}
          {pending && turn.content && <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse bg-slate-400 align-text-bottom" />}
        </div>
        {!isUser && turn.sources.length > 0 && (
          <div className="mt-2 space-y-1.5">
            {turn.sources.map((source) => (
              <details key={source.rank} className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs">
                <summary className="cursor-pointer select-none font-medium text-slate-600">
                  Source {source.rank} - {source.paper_title ? `${source.paper_title} - ` : ""}
                  {source.section_title} (p.{source.page_start}-{source.page_end}) ·{" "}
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
