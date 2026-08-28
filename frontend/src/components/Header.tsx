import { Link, useLocation } from "react-router-dom";

export default function Header() {
  const location = useLocation();
  const onDashboard = location.pathname === "/";

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-lg shadow-sm">
            🧠
          </span>
          <span className="text-lg font-bold tracking-tight text-slate-900">ScholarMind AI</span>
        </Link>
        <nav className="flex items-center gap-1">
          <Link
            to="/"
            className={`rounded-lg px-3.5 py-2 text-sm font-medium transition-colors ${
              onDashboard ? "bg-brand-50 text-brand-700" : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            Library
          </Link>
        </nav>
      </div>
    </header>
  );
}
