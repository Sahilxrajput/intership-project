export default function OutputPane({ output, status }) {
  const isError = status === "error";

  return (
    <div
      className={`mx-4 mb-3 rounded-lg border text-xs font-mono transition-all duration-300 ${
        isError
          ? "border-red-500/20 bg-red-500/5"
          : "border-emerald-500/20 bg-emerald-500/5"
      }`}
    >
      {/* Output header */}
      <div
        className={`flex items-center gap-2 px-3 py-2 border-b ${
          isError ? "border-red-500/15" : "border-emerald-500/15"
        }`}
      >
        <div
          className={`w-1.5 h-1.5 rounded-full ${
            isError ? "bg-red-400" : "bg-emerald-400"
          }`}
        />
        <span
          className={`text-[10px] uppercase tracking-widest font-semibold ${
            isError ? "text-red-400/80" : "text-emerald-400/80"
          }`}
        >
          {isError ? "Error" : "Output"}
        </span>
      </div>

      {/* Output body */}
      <div className="px-3 py-2.5">
        <pre
          className={`whitespace-pre-wrap break-words leading-relaxed ${
            isError ? "text-red-300/90" : "text-slate-300"
          }`}
        >
          {output.text}
        </pre>

        {/* Stderr (if present alongside stdout) */}
        {output.stderr && (
          <div className="mt-2 pt-2 border-t border-yellow-500/20">
            <span className="text-[10px] text-yellow-400/70 uppercase tracking-wider">
              stderr
            </span>
            <pre className="text-yellow-300/80 mt-1 whitespace-pre-wrap break-words">
              {output.stderr}
            </pre>
          </div>
        )}

        {/* Simulation notice */}
        {output.simulated && (
          <div className="mt-2 pt-2 border-t border-slate-700 flex items-start gap-2">
            <svg className="mt-0.5 shrink-0" width="12" height="12" viewBox="0 0 12 12" fill="none">
              <circle cx="6" cy="6" r="5" stroke="#7C6AF7" strokeWidth="1.2"/>
              <path d="M6 4V6.5M6 8V8.3" stroke="#7C6AF7" strokeWidth="1.2" strokeLinecap="round"/>
            </svg>
            <span className="text-[10px] text-slate-500 leading-relaxed">{output.note}</span>
          </div>
        )}
      </div>
    </div>
  );
}
