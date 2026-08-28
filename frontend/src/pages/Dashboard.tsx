import { useCallback, useEffect, useRef, useState } from "react";
import { api, type PaperSummary } from "../api/client";
import UploadDropzone from "../components/UploadDropzone";
import PaperCard from "../components/PaperCard";

const POLL_INTERVAL_MS = 3000;

export default function Dashboard() {
  const [papers, setPapers] = useState<PaperSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
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

  const handleDelete = async (id: string) => {
    setPapers((prev) => prev?.filter((p) => p.id !== id) ?? null);
    try {
      await api.deletePaper(id);
    } catch {
      refresh();
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-10 text-center">
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
        {papers && <span className="text-sm text-slate-400">{papers.length} paper{papers.length === 1 ? "" : "s"}</span>}
      </div>

      <div className="mt-5">
        {error && (
          <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">
            {error} — is the backend running at the configured API URL?
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
          <div className="rounded-2xl border border-dashed border-slate-200 py-16 text-center text-slate-400">
            No papers yet — upload one above to get started.
          </div>
        )}

        {!error && papers && papers.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {papers.map((paper) => (
              <PaperCard key={paper.id} paper={paper} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
