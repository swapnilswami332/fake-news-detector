import { useEffect, useState } from "react";

import { HomePage } from "./pages/HomePage";

export default function App() {
  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem("truthlens-theme") === "dark"
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("truthlens-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-slate-50 text-ink transition-colors dark:bg-slate-950 dark:text-slate-100">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-4 py-5 sm:px-6">
        <span className="font-bold tracking-tight">TruthLens</span>
        <button
          onClick={() => setDarkMode((enabled) => !enabled)}
          className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold dark:border-slate-700"
          aria-label="Toggle dark mode"
        >
          {darkMode ? "Light mode" : "Dark mode"}
        </button>
      </nav>
      <HomePage />
      <footer className="mx-auto max-w-5xl px-4 pb-8 text-xs text-slate-500 sm:px-6">
        TruthLens is an educational tool and does not replace professional reporting or fact-checking.
      </footer>
    </div>
  );
}
