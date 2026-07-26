import type { Prediction } from "../types";

type ResultCardProps = {
  result: Prediction;
  onCopy: () => void;
  copied: boolean;
};

export function ResultCard({ result, onCopy, copied }: ResultCardProps) {
  const isFake = result.prediction === "Fake";
  const tone = isFake
    ? "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-900 dark:bg-rose-950/40 dark:text-rose-200"
    : "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200";

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-7">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">Assessment</p>
          <div className="mt-1 flex items-center gap-3">
            <span className={`rounded-full border px-3 py-1 text-sm font-bold ${tone}`}>
              Likely {result.prediction}
            </span>
            <span className="text-xs text-slate-500">{result.processing_time_ms} ms</span>
          </div>
        </div>
        <button
          onClick={onCopy}
          className="rounded-lg border border-slate-300 px-3 py-2 text-xs font-semibold transition hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
        >
          {copied ? "Copied" : "Copy result"}
        </button>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2">
        <Metric label="Model confidence" value={result.confidence} color={isFake ? "bg-rose-500" : "bg-emerald-500"} />
        <Metric label="Credibility score" value={result.trust_score} color="bg-blue-600" />
      </div>

      <div className="mt-6 space-y-4 text-sm leading-6">
        <Insight title="Why the model flagged this" text={result.model_reason} />
        <Insight title="AI fact-check review" text={result.ai_fact_check} />
      </div>

      {result.sources.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold">Sources reviewed</h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {result.sources.map((source) => (
              <a
                key={source.url}
                href={source.url}
                target="_blank"
                rel="noreferrer"
                className="rounded-xl border border-slate-200 p-3 text-sm transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-800 dark:hover:bg-slate-800"
              >
                <span className="line-clamp-2 font-medium">{source.title}</span>
                <span className="mt-1 block truncate text-xs text-blue-600 dark:text-blue-400">
                  {new URL(source.url).hostname}
                </span>
              </a>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}

function Metric({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-sm">
        <span className="text-slate-600 dark:text-slate-300">{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function Insight({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <h3 className="font-semibold">{title}</h3>
      <p className="mt-1 text-slate-600 dark:text-slate-300">{text}</p>
    </div>
  );
}
