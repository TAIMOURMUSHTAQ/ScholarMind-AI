import { Link } from "react-router-dom";
import type { PaperSummary } from "../api/client";

const STATUS_STYLES: Record<PaperSummary["status"], string> = {
  ready: "bg-emerald-50 text-emerald-700",
  processing: "bg-amber-50 text-amber-700",
  failed: "bg-red-50 text-red-700",
};

const STATUS_LABEL: Record<PaperSummary["status"], string> = {
  ready: "Ready",
  processing: "Processing…",
  failed: "Failed",
};

interface Props {
  paper: PaperSummary;
  onDelete: (id: string) => void;
}

export default function PaperCard({ paper, onDelete }: Props) {
  const card = (
    <div className="group flex h-full flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md">
      <div>
        <div className="mb-2 flex items-start justify-between gap-2">
          <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_STYLES[paper.status]}`}>
            {STATUS_LABEL[paper.status]}
          </span>
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onDelete(paper.id);
            }}
            className="rounded-md p-1 text-slate-300 opacity-0 transition-opacity hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
            title="Delete paper"
          >
            ✕
          </button>
        </div>
        <h3 className="line-clamp-2 text-base font-semibold text-slate-900">{paper.title}</h3>
        {paper.authors.length > 0 && (
          <p className="mt-1 line-clamp-1 text-sm text-slate-500">{paper.authors.join(", ")}</p>
        )}
        {paper.status === "failed" && paper.error_message && (
          <p className="mt-2 line-clamp-2 text-xs text-red-600">{paper.error_message}</p>
        )}
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
        <span>{paper.num_pages ? `${paper.num_pages} pages` : "—"}</span>
        <span>{new Date(paper.upload_time).toLocaleDateString()}</span>
      </div>
    </div>
  );

  if (paper.status !== "ready") {
    return <div className="cursor-default">{card}</div>;
  }
  return <Link to={`/papers/${paper.id}`}>{card}</Link>;
}
