import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import type { PaperSummary } from "../api/client";
import { CheckCircleIcon, ClockIcon, AlertTriangleIcon, PencilIcon, TrashIcon } from "./icons";

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

const STATUS_ICON: Record<PaperSummary["status"], typeof CheckCircleIcon> = {
  ready: CheckCircleIcon,
  processing: ClockIcon,
  failed: AlertTriangleIcon,
};

interface Props {
  paper: PaperSummary;
  onRequestDelete: (id: string) => void;
  onRename: (id: string, title: string) => void;
  compareMode?: boolean;
  selected?: boolean;
  onToggleSelect?: (id: string) => void;
}

export default function PaperCard({ paper, onRequestDelete, onRename, compareMode, selected, onToggleSelect }: Props) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(paper.title);
  const inputRef = useRef<HTMLInputElement>(null);
  const StatusIcon = STATUS_ICON[paper.status];

  useEffect(() => {
    if (editing) inputRef.current?.focus();
  }, [editing]);

  const commitRename = () => {
    setEditing(false);
    const trimmed = draft.trim();
    if (trimmed && trimmed !== paper.title) onRename(paper.id, trimmed);
  };

  const inner = (
    <div
      className={`group flex h-full flex-col justify-between rounded-2xl border bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md ${
        selected ? "border-brand-400 ring-2 ring-brand-100" : "border-slate-200"
      }`}
    >
      <div>
        <div className="mb-2 flex items-start justify-between gap-2">
          <div className="flex items-center gap-2">
            {compareMode && paper.status === "ready" && (
              <input
                type="checkbox"
                checked={!!selected}
                onChange={(e) => {
                  e.stopPropagation();
                  onToggleSelect?.(paper.id);
                }}
                onClick={(e) => e.stopPropagation()}
                className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-400"
              />
            )}
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${STATUS_STYLES[paper.status]}`}>
              <StatusIcon className="h-3 w-3" strokeWidth={2.25} />
              {STATUS_LABEL[paper.status]}
            </span>
          </div>
          {!compareMode && (
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onRequestDelete(paper.id);
              }}
              className="rounded-md p-1.5 text-slate-300 opacity-0 transition-opacity hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
              title="Delete paper"
            >
              <TrashIcon className="h-4 w-4" />
            </button>
          )}
        </div>

        {editing ? (
          <input
            ref={inputRef}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onClick={(e) => e.preventDefault()}
            onBlur={commitRename}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitRename();
              if (e.key === "Escape") setEditing(false);
            }}
            className="w-full rounded-md border border-brand-300 px-1.5 py-0.5 text-base font-semibold text-slate-900 outline-none focus:ring-2 focus:ring-brand-100"
          />
        ) : (
          <div className="flex items-start gap-1.5">
            <h3 className="line-clamp-2 text-base font-semibold text-slate-900">{paper.title}</h3>
            {!compareMode && (
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setDraft(paper.title);
                  setEditing(true);
                }}
                title="Rename"
                className="mt-0.5 shrink-0 rounded p-0.5 text-slate-300 opacity-0 transition-opacity hover:text-slate-500 group-hover:opacity-100"
              >
                <PencilIcon className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        )}

        {paper.authors.length > 0 && (
          <p className="mt-1 line-clamp-1 text-sm text-slate-500">{paper.authors.join(", ")}</p>
        )}
        {paper.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {paper.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-medium text-brand-700">
                {tag}
              </span>
            ))}
          </div>
        )}
        {paper.status === "failed" && paper.error_message && (
          <p className="mt-2 line-clamp-2 text-xs text-red-600">{paper.error_message}</p>
        )}
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
        <span>{paper.num_pages ? `${paper.num_pages} pages` : "-"}</span>
        <span>{new Date(paper.upload_time).toLocaleDateString()}</span>
      </div>
    </div>
  );

  if (paper.status !== "ready" || editing) {
    return <div className="cursor-default">{inner}</div>;
  }

  if (compareMode) {
    return (
      <div className="cursor-pointer" onClick={() => onToggleSelect?.(paper.id)}>
        {inner}
      </div>
    );
  }

  return <Link to={`/papers/${paper.id}`}>{inner}</Link>;
}
