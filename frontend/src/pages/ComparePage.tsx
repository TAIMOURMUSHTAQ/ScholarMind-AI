import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, compareChatBase, type PaperSummary } from "../api/client";
import ChatPanel from "../components/ChatPanel";
import { ArrowLeftIcon } from "../components/icons";

export default function ComparePage() {
  const { ids } = useParams<{ ids: string }>();
  const navigate = useNavigate();
  const [papers, setPapers] = useState<PaperSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const paperIds = (ids ?? "").split(",").filter(Boolean);

  useEffect(() => {
    if (paperIds.length < 2) {
      setError("Select at least two papers to compare.");
      return;
    }
    Promise.all(paperIds.map((id) => api.getPaper(id)))
      .then(setPapers)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load the selected papers."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ids]);

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16 text-center">
        <p className="text-lg font-semibold text-red-600">{error}</p>
        <button onClick={() => navigate("/")} className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:underline">
          <ArrowLeftIcon className="h-4 w-4" /> Back to library
        </button>
      </div>
    );
  }

  if (!papers) {
    return (
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="h-64 animate-pulse rounded-2xl bg-slate-100" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-4 px-6 py-8">
      <button onClick={() => navigate("/")} className="flex items-center gap-1.5 self-start text-sm font-medium text-slate-400 hover:text-slate-700">
        <ArrowLeftIcon className="h-4 w-4" /> Back to library
      </button>

      <div className="flex flex-wrap gap-2">
        {papers.map((paper) => (
          <span key={paper.id} className="rounded-full bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700">
            {paper.title}
          </span>
        ))}
      </div>

      <div className="h-[calc(100vh-12rem)] min-h-[500px]">
        <ChatPanel
          basePath={compareChatBase(paperIds)}
          title={`Comparing ${papers.length} papers`}
          subtitle="Answers cite which paper each point comes from."
        />
      </div>
    </div>
  );
}
