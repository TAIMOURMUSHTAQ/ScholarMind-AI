import { Link, useLocation } from "react-router-dom";
import { LogoMark } from "./icons";

export default function Header() {
  const location = useLocation();
  const onDashboard = location.pathname === "/";

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3.5">
        <Link to="/" className="flex items-center gap-2.5">
          <LogoMark className="h-8 w-8 shadow-sm rounded-[9px]" />
          <span className="text-[17px] font-bold tracking-tight text-slate-900">
            ScholarMind <span className="text-brand-600">AI</span>
          </span>
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
