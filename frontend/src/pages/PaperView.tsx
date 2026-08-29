import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, figureImageUrl, paperChatBase, type Figure, type PaperDetail, type RelatedPaper } from "../api/client";
import ChatPanel from "../components/ChatPanel";
import FigureLightbox from "../components/FigureLightbox";
import { ArrowLeftIcon, PencilIcon } from "../components/icons";

const INSIGHT_POLL_MS = 3000;

export default function PaperView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");
  const titleInputRef = useRef<HTMLInputElement>(null);
  const [relatedPapers, setRelatedPapers] = useState<RelatedPaper[] | null>(null);
  const [relatedLoading, setRelatedLoading] = useState(false);
  const [openFigure, setOpenFigure] = useState<Figure | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .getPaper(id)
      .then(setPaper)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load paper."));
  }, [id]);

  useEffect(() => {
    if (!id || paper?.status !== "ready") return;
    setRelatedLoading(true);
    api
      .getRelatedPapers(id)
      .then(setRelatedPapers)
      .catch(() => setRelatedPapers([]))
      .finally(() => setRelatedLoading(false));
  }, [id, paper?.status]);

  useEffect(() => {
    if (!id || paper?.insight_status !== "pending") return;
    const interval = setInterval(() => {
      api.getPaper(id).then(setPaper).catch(() => undefined);
    }, INSIGHT_POLL_MS);
    return () => clearInterval(interval);
  }, [id, paper?.insight_status]);

  useEffect(() => {
    if (editingTitle) titleInputRef.current?.focus();
  }, [editingTitle]);

  const startEditingTitle = () => {
    if (!paper) return;
    setTitleDraft(paper.title);
    setEditingTitle(true);
  };

  const saveTitle = async () => {
    const newTitle = titleDraft.trim();
    setEditingTitle(false);
    if (!id || !paper || !newTitle || newTitle === paper.title) return;
    try {
      await api.renamePaper(id, newTitle);
      setPaper({ ...paper, title: newTitle });
    } catch {
      /* leave the old title displayed on failure */
    }
  };

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16 text-center">
        <p className="text-lg font-semibold text-red-600">{error}</p>
        <Link to="/" className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:underline">
          <ArrowLeftIcon className="h-4 w-4" /> Back to library
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
        <button onClick={() => navigate("/")} className="flex items-center gap-1.5 text-sm font-medium text-slate-400 hover:text-slate-700">
          <ArrowLeftIcon className="h-4 w-4" /> Back to library
        </button>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          {editingTitle ? (
            <input
              ref={titleInputRef}
              value={titleDraft}
              onChange={(e) => setTitleDraft(e.target.value)}
              onBlur={saveTitle}
              onKeyDown={(e) => {
                if (e.key === "Enter") saveTitle();
                if (e.key === "Escape") setEditingTitle(false);
              }}
              className="w-full rounded-lg border border-brand-300 px-2 py-1 text-xl font-bold leading-snug text-slate-900 outline-none focus:ring-2 focus:ring-brand-100"
            />
          ) : (
            <div className="group flex items-start gap-2">
              <h1 className="text-xl font-bold leading-snug text-slate-900">{paper.title}</h1>
              <button
                onClick={startEditingTitle}
                title="Rename"
                className="mt-1 shrink-0 rounded p-0.5 text-slate-300 opacity-0 transition-opacity hover:text-slate-500 group-hover:opacity-100"
              >
                <PencilIcon className="h-4 w-4" />
              </button>
            </div>
          )}
          {paper.authors.length > 0 && <p className="mt-2 text-sm text-slate-500">{paper.authors.join(", ")}</p>}

          <div className="mt-4 flex flex-wrap gap-2">
            {paper.metadata.year && <Chip label={paper.metadata.year} />}
            {paper.metadata.venue && <Chip label={paper.metadata.venue} />}
            {paper.metadata.doi && <Chip label={`DOI: ${paper.metadata.doi}`} />}
            <Chip label={`${paper.num_pages} pages`} />
            <Chip label={`${paper.num_chunks} indexed chunks`} />
          </div>

          {paper.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {paper.tags.map((tag) => (
                <span key={tag} className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700">
                  {tag}
                </span>
              ))}
            </div>
          )}

          <InsightCardSection status={paper.insight_status} card={paper.insight_card} />

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
                {paper.section_titles.map((title, i) => (
                  <li key={`${i}-${title}`} className="truncate">
                    · {title}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {paper.figures.length > 0 && (
            <div className="mt-5">
              <h2 className="text-sm font-semibold text-slate-700">Figures</h2>
              <div className="mt-1.5 grid grid-cols-3 gap-2">
                {paper.figures.map((figure) => (
                  <button
                    key={figure.id}
                    onClick={() => setOpenFigure(figure)}
                    className="group overflow-hidden rounded-lg border border-slate-200 transition-colors hover:border-brand-300"
                  >
                    <img
                      src={figureImageUrl(id, figure.id)}
                      alt={figure.caption || `Figure on page ${figure.page + 1}`}
                      className="h-20 w-full object-cover transition-transform group-hover:scale-105"
                    />
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <RelatedWorkSection loading={relatedLoading} papers={relatedPapers} />
      </div>

      <div className="h-[calc(100vh-8rem)] min-h-[500px] lg:sticky lg:top-24">
        <ChatPanel basePath={paperChatBase(id)} />
      </div>

      {openFigure && <FigureLightbox paperId={id} figure={openFigure} onClose={() => setOpenFigure(null)} />}
    </div>
  );
}

function RelatedWorkSection({ loading, papers }: { loading: boolean; papers: RelatedPaper[] | null }) {
  if (loading) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-700">Related work</h2>
        <div className="mt-3 space-y-2">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-14 animate-pulse rounded-lg bg-slate-100" />
          ))}
        </div>
      </div>
    );
  }

  if (!papers || papers.length === 0) return null;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-sm font-semibold text-slate-700">Related work</h2>
      <p className="mt-0.5 text-xs text-slate-400">Found via Semantic Scholar</p>
      <div className="mt-3 space-y-3">
        {papers.map((related, i) => (
          <a
            key={i}
            href={related.url || undefined}
            target="_blank"
            rel="noreferrer"
            className={`block rounded-lg border border-slate-100 p-3 transition-colors ${
              related.url ? "hover:border-brand-200 hover:bg-brand-50/40" : "cursor-default"
            }`}
          >
            <p className="text-sm font-medium text-slate-800">{related.title}</p>
            <p className="mt-0.5 text-xs text-slate-400">
              {related.authors.slice(0, 3).join(", ")}
              {related.authors.length > 3 ? " et al." : ""}
              {related.year ? ` · ${related.year}` : ""}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}

function InsightCardSection({ status, card }: { status: PaperDetail["insight_status"]; card: PaperDetail["insight_card"] }) {
  if (status === "unavailable") return null;

  if (status === "pending" || !card) {
    return (
      <div className="mt-5 rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-3">
        <p className="flex items-center gap-2 text-xs font-medium text-slate-400">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand-400" />
          Generating AI insights…
        </p>
      </div>
    );
  }

  const sections: { label: string; content: string | string[] }[] = [
    { label: "Problem", content: card.problem },
    { label: "Method", content: card.method },
    { label: "Key results", content: card.key_results },
    { label: "Limitations", content: card.limitations },
    { label: "Contributions", content: card.contributions },
  ].filter((s) => (Array.isArray(s.content) ? s.content.length > 0 : Boolean(s.content)));

  if (sections.length === 0) return null;

  return (
    <div className="mt-5 rounded-xl border border-brand-100 bg-brand-50/40 p-4">
      <h2 className="text-xs font-bold uppercase tracking-wide text-brand-700">AI insight card</h2>
      <div className="mt-2.5 space-y-2.5">
        {sections.map(({ label, content }) => (
          <div key={label}>
            <h3 className="text-xs font-semibold text-slate-700">{label}</h3>
            {Array.isArray(content) ? (
              <ul className="mt-0.5 space-y-0.5 text-sm text-slate-600">
                {content.map((item, i) => (
                  <li key={i}>· {item}</li>
                ))}
              </ul>
            ) : (
              <p className="mt-0.5 text-sm text-slate-600">{content}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function Chip({ label }: { label: string }) {
  return (
    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{label}</span>
  );
}
