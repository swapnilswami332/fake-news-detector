import { useState } from "react";
import axios from "axios";

import { InputPanel } from "../components/InputPanel";
import { ResultCard } from "../components/ResultCard";
import { API_BASE } from "../config";
import type { Prediction } from "../types";

type HistoryItem = Pick<Prediction, "prediction" | "confidence"> & { text: string };

export function HomePage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function analyze() {
    setError("");
    setCopied(false);
    setIsLoading(true);

    try {
      const response = await axios.post<Prediction>(`${API_BASE}/predict`, { text });
      setResult(response.data);
      setHistory((items) =>
        [{ text, prediction: response.data.prediction, confidence: response.data.confidence }, ...items].slice(0, 5)
      );
    } catch (requestError) {
      const detail = axios.isAxiosError(requestError)
        ? requestError.response?.data?.detail
        : null;
      setError(typeof detail === "string" ? detail : "Could not analyze this text. Check that the API is running.");
    } finally {
      setIsLoading(false);
    }
  }

  async function copyResult() {
    if (!result) return;
    const summary = `TruthLens: Likely ${result.prediction} (${result.confidence}% confidence)\nCredibility score: ${result.trust_score}/100\n${result.model_reason}\n${result.ai_fact_check}`;
    await navigator.clipboard.writeText(summary);
    setCopied(true);
  }

  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 sm:py-16">
      <header className="mb-10 max-w-2xl">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-accent">TruthLens</p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
          A second look at the news you read.
        </h1>
        <p className="mt-4 text-base leading-7 text-slate-600 dark:text-slate-300">
          Language-pattern classification combined with source-aware AI review. Treat every result as a starting point, not a verdict.
        </p>
      </header>

      <InputPanel text={text} isLoading={isLoading} onChange={setText} onAnalyze={analyze} />

      {error && (
        <p role="alert" className="mt-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-6">
          <ResultCard result={result} onCopy={copyResult} copied={copied} />
        </div>
      )}

      {history.length > 0 && (
        <section className="mt-10">
          <h2 className="text-sm font-semibold">This session</h2>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {history.map((item, index) => (
              <button
                key={`${item.text}-${index}`}
                onClick={() => setText(item.text)}
                className="rounded-xl border border-slate-200 bg-white p-3 text-left text-sm transition hover:border-blue-300 dark:border-slate-800 dark:bg-slate-900"
              >
                <span className="font-semibold">Likely {item.prediction} · {item.confidence}%</span>
                <span className="mt-1 block truncate text-xs text-slate-500">{item.text}</span>
              </button>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
