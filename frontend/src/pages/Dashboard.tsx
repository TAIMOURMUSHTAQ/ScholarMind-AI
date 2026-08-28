import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type PaperSummary } from "../api/client";
import UploadDropzone from "../components/UploadDropzone";
import PaperCard from "../components/PaperCard";
import ConfirmDialog from "../components/ConfirmDialog";
import { AlertTriangleIcon, DocumentIcon, LayersIcon } from "../components/icons";

const POLL_INTERVAL_MS = 3000;

export default function Dashboard() {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<PaperSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await api.listPapers();
      setPapers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not reach the backend.");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const hasProcessing = papers?.some((p) => p.status === "processing");
    if (hasProcessing) {
      pollRef.current = setInterval(refresh, POLL_INTERVAL_MS);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [papers, refresh]);

  const handleUpload = async (file: File) => {
    await api.uploadPaper(file);
    await refresh();
  };

  const confirmDelete = async () => {
    const id = pendingDeleteId;
    setPendingDeleteId(null);
    if (!id) return;
    setPapers((prev) => prev?.filter((p) => p.id !== id) ?? null);
    try {
      await api.deletePaper(id);
    } catch {
      refresh();
    }
  };

  const handleRename = async (id: string, title: string) => {
    setPapers((prev) => prev?.map((p) => (p.id === id ? { ...p, title } : p)) ?? null);
    try {
      await api.renamePaper(id, title);
    } catch {
      refresh();
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const exitCompareMode = () => {
    setCompareMode(false);
    setSelectedIds([]);
  };

  const paperBeingDeleted = papers?.find((p) => p.id === pendingDeleteId);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="relative mb-10 text-center">
        <div
          aria-hidden
          className="pointer-events-none absolute left-1/2 top-1/2 -z-10 h-72 w-[36rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-br from-brand-200/50 via-brand-100/40 to-transparent blur-3xl"
        />
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
          Read less. Understand more.
        </h1>
        <p className="mx-auto mt-2 max-w-xl text-slate-500">
          Upload a research paper and ScholarMind AI will extract its key details and let you chat with it directly.
        </p>
      </div>

      <div className="mx-auto mb-14 max-w-2xl">
        <UploadDropzone onUpload={handleUpload} />
      </div>

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">Your Library</h2>
        <div className="flex items-center gap-3">
          {papers && !compareMode && <span className="text-sm text-slate-400">{papers.length} paper{papers.length === 1 ? "" : "s"}</span>}
          {papers && papers.filter((p) => p.status === "ready").length >= 2 && (
            <button
              onClick={() => (compareMode ? exitCompareMode() : setCompareMode(true))}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                compareMode ? "bg-slate-100 text-slate-600 hover:bg-slate-200" : "border border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
            >
              <LayersIcon className="h-4 w-4" />
              {compareMode ? "Cancel" : "Compare papers"}
            </button>
          )}
        </div>
      </div>

      <div className="mt-5">
        {error && (
          <div className="flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
            <AlertTriangleIcon className="h-4 w-4 shrink-0" />
            {error} - is the backend running at the configured API URL?
          </div>
        )}

        {!error && papers === null && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-36 animate-pulse rounded-2xl bg-slate-100" />
            ))}
          </div>
        )}

        {!error && papers?.length === 0 && (
          <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-slate-200 py-16 text-center text-slate-400">
            <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
              <DocumentIcon className="h-6 w-6" />
            </span>
            No papers yet, upload one above to get started.
          </div>
        )}

        {!error && papers && papers.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {papers.map((paper) => (
              <PaperCard
                key={paper.id}
                paper={paper}
                onRequestDelete={setPendingDeleteId}
                onRename={handleRename}
                compareMode={compareMode}
                selected={selectedIds.includes(paper.id)}
                onToggleSelect={toggleSelect}
              />
            ))}
          </div>
        )}
      </div>

      {compareMode && selectedIds.length >= 2 && (
        <div className="fixed inset-x-0 bottom-6 z-20 flex justify-center">
          <button
            onClick={() => navigate(`/compare/${selectedIds.join(",")}`)}
            className="flex items-center gap-2 rounded-full bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition-colors hover:bg-brand-700"
          >
            <LayersIcon className="h-4 w-4" />
            Compare {selectedIds.length} papers
          </button>
        </div>
      )}

      <ConfirmDialog
        open={pendingDeleteId !== null}
        title="Delete this paper?"
        message={
          paperBeingDeleted
            ? `"${paperBeingDeleted.title}" and its chat history will be permanently removed. This can't be undone.`
            : "This can't be undone."
        }
        confirmLabel="Delete"
        danger
        onConfirm={confirmDelete}
        onCancel={() => setPendingDeleteId(null)}
      />
    </div>
  );
}
