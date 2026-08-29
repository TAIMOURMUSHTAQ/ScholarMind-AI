import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type LibrarySearchResult, type PaperSummary } from "../api/client";
import UploadDropzone from "../components/UploadDropzone";
import ArxivImportBar from "../components/ArxivImportBar";
import PaperCard from "../components/PaperCard";
import ConfirmDialog from "../components/ConfirmDialog";
import { AlertTriangleIcon, DocumentIcon, LayersIcon, SearchIcon } from "../components/icons";

const POLL_INTERVAL_MS = 3000;
const SEARCH_DEBOUNCE_MS = 400;

export default function Dashboard() {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<PaperSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<LibrarySearchResult[] | null>(null);
  const [searching, setSearching] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const searchDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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

  useEffect(() => {
    if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
    const query = searchQuery.trim();
    if (query.length < 3) {
      setSearchResults(null);
      setSearching(false);
      return;
    }
    setSearching(true);
    searchDebounceRef.current = setTimeout(async () => {
      try {
        const results = await api.searchLibrary(query);
        setSearchResults(results);
      } catch {
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, SEARCH_DEBOUNCE_MS);
    return () => {
      if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);
    };
  }, [searchQuery]);

  const allTags = useMemo(() => {
    const seen = new Set<string>();
    for (const paper of papers ?? []) for (const tag of paper.tags) seen.add(tag);
    return Array.from(seen).sort();
  }, [papers]);

  const visiblePapers = useMemo(() => {
    if (!papers) return null;
    if (!activeTag) return papers;
    return papers.filter((p) => p.tags.includes(activeTag));
  }, [papers, activeTag]);

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
  const showingSearch = searchQuery.trim().length >= 3;

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

      <div className="mx-auto mb-10 max-w-2xl">
        <UploadDropzone onUpload={handleUpload} />
        <ArxivImportBar onImported={refresh} />
      </div>

      <div className="mx-auto mb-10 max-w-2xl">
        <div className="relative">
          <SearchIcon className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search across every paper in your library…"
            className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
          />
        </div>
      </div>

      {showingSearch ? (
        <SearchResults searching={searching} results={searchResults} onClear={() => setSearchQuery("")} />
      ) : (
        <>
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

          {allTags.length > 0 && !compareMode && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {allTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => setActiveTag((prev) => (prev === tag ? null : tag))}
                  className={`rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
                    activeTag === tag
                      ? "border-brand-500 bg-brand-600 text-white"
                      : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          )}

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

            {!error && visiblePapers && visiblePapers.length > 0 && (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {visiblePapers.map((paper) => (
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

            {!error && papers && papers.length > 0 && visiblePapers?.length === 0 && (
              <p className="py-10 text-center text-sm text-slate-400">No papers tagged "{activeTag}".</p>
            )}
          </div>
        </>
      )}

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

function SearchResults({
  searching,
  results,
  onClear,
}: {
  searching: boolean;
  results: LibrarySearchResult[] | null;
  onClear: () => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">Search results</h2>
        <button onClick={onClear} className="text-sm font-medium text-slate-400 hover:text-slate-700">
          Clear
        </button>
      </div>

      <div className="mt-5 space-y-3">
        {searching && (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100" />
            ))}
          </div>
        )}

        {!searching && results?.length === 0 && (
          <p className="py-10 text-center text-sm text-slate-400">No matching passages found in your library.</p>
        )}

        {!searching &&
          results?.map((result, i) => (
            <Link
              key={i}
              to={`/papers/${result.paper_id}`}
              className="block rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-semibold text-slate-900">{result.paper_title}</span>
                <span className="shrink-0 text-xs text-slate-400">{Math.round(result.score * 100)}% match</span>
              </div>
              <p className="mt-1 text-xs font-medium text-slate-500">
                {result.section_title} · p.{result.page_start}-{result.page_end}
              </p>
              <p className="mt-1.5 line-clamp-2 text-sm text-slate-600">{result.preview}…</p>
            </Link>
          ))}
      </div>
    </div>
  );
}
