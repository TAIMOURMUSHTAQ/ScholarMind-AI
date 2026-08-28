import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import PaperView from "./pages/PaperView";
import ComparePage from "./pages/ComparePage";

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/papers/:id" element={<PaperView />} />
          <Route path="/compare/:ids" element={<ComparePage />} />
        </Routes>
      </main>
    </div>
  );
}
