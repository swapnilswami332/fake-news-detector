type InputPanelProps = {
  text: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onAnalyze: () => void;
};

export function InputPanel({
  text,
  isLoading,
  onChange,
  onAnalyze
}: InputPanelProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:p-7">
      <label htmlFor="article" className="mb-2 block text-sm font-semibold">
        Headline or article
      </label>
      <textarea
        id="article"
        value={text}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Paste a news headline or article here. TruthLens will look at language signals and compare the central claim with search results."
        className="min-h-48 w-full resize-y rounded-xl border border-slate-300 bg-slate-50 p-4 text-sm leading-6 outline-none transition focus:border-accent focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-950 dark:focus:ring-blue-950"
        disabled={isLoading}
      />
      <div className="mt-4 flex items-center justify-between gap-4">
        <p className="text-xs text-slate-500">{text.length.toLocaleString()} characters</p>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={isLoading || text.trim().length < 20}
          className="inline-flex min-w-32 items-center justify-center rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Analyzing
            </>
          ) : (
            "Analyze"
          )}
        </button>
      </div>
    </section>
  );
}
