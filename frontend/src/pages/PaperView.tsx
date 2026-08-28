import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, type PaperDetail } from "../api/client";
import ChatPanel from "../components/ChatPanel";

export default function PaperView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .getPaper(id)
      .then(setPaper)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load paper."));
  }, [id]);

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16 text-center">
        <p className="text-lg font-semibold text-red-600">{error}</p>
        <Link to="/" className="mt-4 inline-block text-sm font-medium text-brand-600 hover:underline">
          ← Back to library
        </Link>
      </div>
    );
  }

  if (!paper || !id) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="h-64 animate-pulse rounded-2xl bg-slate-100" />
      </div>
    );
  }

  return (
    <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 py-8 lg:grid-cols-[1.1fr_1.4fr]">
      <div className="space-y-4">
        <button onClick={() => navigate("/")} className="text-sm font-medium text-slate-400 hover:text-slate-700">
          ← Back to library
        </button>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-xl font-bold leading-snug text-slate-900">{paper.title}</h1>
          {paper.authors.length > 0 && <p className="mt-2 text-sm text-slate-500">{paper.authors.join(", ")}</p>}

          <div className="mt-4 flex flex-wrap gap-2">
            {paper.metadata.year && <Chip label={paper.metadata.year} />}
            {paper.metadata.venue && <Chip label={paper.metadata.venue} />}
            {paper.metadata.doi && <Chip label={`DOI: ${paper.metadata.doi}`} />}
            <Chip label={`${paper.num_pages} pages`} />
            <Chip label={`${paper.num_chunks} indexed chunks`} />
          </div>

          <div className="mt-5">
            <h2 className="text-sm font-semibold text-slate-700">Abstract</h2>
            <p className="mt-1.5 max-h-64 overflow-y-auto whitespace-pre-line text-sm leading-relaxed text-slate-600">
              {paper.abstract || "No abstract could be extracted from this paper."}
            </p>
          </div>

          {paper.section_titles.length > 0 && (
            <div className="mt-5">
              <h2 className="text-sm font-semibold text-slate-700">Sections</h2>
              <ul className="mt-1.5 space-y-1 text-sm text-slate-500">
                {paper.section_titles.map((title) => (
                  <li key={title} className="truncate">
                    · {title}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="h-[calc(100vh-8rem)] min-h-[500px] lg:sticky lg:top-24">
        <ChatPanel paperId={id} />
      </div>
    </div>
  );
}

function Chip({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{label}</span>
  );
}
