import { useCallback, useRef, useState } from "react";

interface Props {
  onUpload: (file: File) => Promise<void>;
}

export default function UploadDropzone({ onUpload }: Props) {
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(
    async (file: File | undefined) => {
      if (!file) return;
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setError("Only PDF files are supported.");
        return;
      }
      setError(null);
      setBusy(true);
      try {
        await onUpload(file);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed.");
      } finally {
        setBusy(false);
      }
    },
    [onUpload]
  );

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFile(e.dataTransfer.files?.[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-8 py-14 text-center transition-colors ${
          dragging ? "border-brand-500 bg-brand-50" : "border-slate-300 bg-white hover:border-brand-400 hover:bg-slate-50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        {busy ? (
          <>
            <div className="h-9 w-9 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
            <p className="text-sm font-medium text-slate-600">Uploading &amp; starting analysis&hellip;</p>
          </>
        ) : (
          <>
            <span className="text-4xl">📄</span>
            <p className="text-base font-semibold text-slate-800">Drop a research paper PDF here</p>
            <p className="text-sm text-slate-500">or click to browse, we'll parse it and get it ready to chat with</p>
          </>
        )}
      </div>
      {error && (
        <p className="mt-3 rounded-lg bg-red-50 px-4 py-2 text-sm font-medium text-red-700">{error}</p>
      )}
    </div>
  );
}
