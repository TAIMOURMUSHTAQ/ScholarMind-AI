import { useState } from "react";
import { api, ApiError, figureImageUrl, type Figure } from "../api/client";
import { XIcon } from "./icons";

interface Props {
  paperId: string;
  figure: Figure;
  onClose: () => void;
}

interface QaTurn {
  question: string;
  answer: string;
}

export default function FigureLightbox({ paperId, figure, onClose }: Props) {
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turns, setTurns] = useState<QaTurn[]>([]);

  const ask = async () => {
    const q = question.trim();
    if (!q || asking) return;
    setAsking(true);
    setError(null);
    setQuestion("");
    try {
      const { answer } = await api.askAboutFigure(paperId, figure.id, q);
      setTurns((prev) => [...prev, { question: q, answer }]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not get an answer for this figure.");
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4" onClick={onClose}>
      <div
        className="flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-slate-100 px-5 py-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">{figure.caption || `Figure (page ${figure.page + 1})`}</h3>
            <p className="text-xs text-slate-400">Page {figure.page + 1}</p>
          </div>
          <button onClick={onClose} className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700">
            <XIcon className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          <img src={figureImageUrl(paperId, figure.id)} alt={figure.caption || "Figure"} className="mx-auto max-h-96 rounded-lg border border-slate-100 object-contain" />

          <div className="mt-4 space-y-3">
            {turns.map((turn, i) => (
              <div key={i} className="space-y-1">
                <p className="rounded-xl bg-brand-600 px-3 py-2 text-sm text-white self-end w-fit ml-auto">{turn.question}</p>
                <p className="rounded-xl bg-slate-100 px-3 py-2 text-sm text-slate-700">{turn.answer}</p>
              </div>
            ))}
            {asking && <p className="text-xs text-slate-400">Thinking…</p>}
            {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{error}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2 border-t border-slate-100 p-4">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder="Ask about this figure…"
            className="flex-1 rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
          />
          <button
            onClick={ask}
            disabled={asking || !question.trim()}
            className="rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
          >
            Ask
          </button>
        </div>
      </div>
    </div>
  );
}
