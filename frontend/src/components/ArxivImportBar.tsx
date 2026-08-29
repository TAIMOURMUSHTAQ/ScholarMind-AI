import { useState } from "react";
import { api, ApiError } from "../api/client";

interface Props {
  onImported: () => void;
}

export default function ArxivImportBar({ onImported }: Props) {
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    const trimmed = value.trim();
    if (!trimmed || busy) return;
    setBusy(true);
    setError(null);
    try {
      await api.importArxiv(trimmed);
      setValue("");
      onImported();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not import from arXiv.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mt-3">
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-400">or import from arXiv:</span>
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="arXiv id or URL, e.g. 2301.12345"
          className="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-xs outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
        />
        <button
          onClick={submit}
          disabled={busy || !value.trim()}
          className="rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-200"
        >
          {busy ? "Importing…" : "Import"}
        </button>
      </div>
      {error && <p className="mt-1.5 text-xs font-medium text-red-600">{error}</p>}
    </div>
  );
}
