export default function TopBar({ languages, selected, onSelect }) {
  return (
    <header className="border-b border-[#2A2D3E] bg-[#0F1117] sticky top-0 z-50">
      <div className="max-w-screen mx-auto px-8 h-14 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-[#7C6AF7] flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 3.5L5.5 7L2 10.5" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M7.5 10.5H12" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
            </svg>
          </div>
          <span className="text-sm font-semibold text-slate-100 tracking-tight">RunCell</span>
        </div>

        {/* Language Switcher */}
        <div className="flex items-center gap-1 bg-[#1A1D27] rounded-lg p-1 border border-[#2A2D3E]">
          {languages.map((lang) => (
            <button
              key={lang}
              onClick={() => onSelect(lang)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold tracking-wide transition-all duration-150 ${
                selected === lang
                  ? "bg-[#7C6AF7] text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-[#2A2D3E]"
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
