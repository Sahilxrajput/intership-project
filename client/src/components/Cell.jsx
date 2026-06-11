import Editor from "@monaco-editor/react";
import OutputPane from "./OutputPane";
import RunButton from "./RunButton";
import { useEffect } from "react";

const EDITOR_OPTIONS = {
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  fontSize: 13.5,
  fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  fontLigatures: true,
  lineHeight: 22,
  padding: { top: 14, bottom: 14 },
  renderLineHighlight: "none",
  overviewRulerLanes: 0,
  hideCursorInOverviewRuler: true,
  scrollbar: { vertical: "hidden", horizontal: "hidden" },
  wordWrap: "on",
  tabSize: 2,
  bracketPairColorization: { enabled: true },
  cursorBlinking: "smooth",
  smoothScrolling: true,
};

export default function Cell({
  cell,
  index,
  language,
  onCodeChange,
  onRun,
  onAddAfter,
  onDelete,
  canDelete,
}) {
  const lineCount = cell.code.split("\n").length;
  // Dynamic height: min 120px, max 480px, ~22px per line + padding
  const editorHeight = Math.min(Math.max(lineCount * 22 + 30, 120), 480);

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      onRun();
    }
  };


  return (
    <div
      className={`group relative rounded-xl border transition-all duration-200 ${
        cell.status === "running"
          ? "border-[#7C6AF7]/60 shadow-[0_0_0_1px_rgba(124,106,247,0.15)]"
          : cell.status === "error"
            ? "border-[#2A2D3E] hover:border-red-500/30"
            : cell.status === "success"
              ? "border-[#2A2D3E] hover:border-[#7C6AF7]/40"
              : "border-[#2A2D3E] hover:border-[#3A3D50]"
      } bg-[#1A1D27]`}
    >
      {/* Left accent bar */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl transition-all duration-300 ${
          cell.status === "running"
            ? "bg-[#7C6AF7] animate-pulse"
            : cell.status === "error"
              ? "bg-red-500/70"
              : cell.status === "success"
                ? "bg-emerald-500/70"
                : "bg-transparent group-hover:bg-[#2A2D3E]"
        }`}
      />

      {/* Cell Header */}
      <div className="flex items-center justify-between px-4 pt-3 pb-1">
        <span className="text-[10px] font-mono text-slate-500 select-none tracking-widest uppercase">
          [{index + 1}] {language.full}
        </span>

        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
          {canDelete && (
            <button
              onClick={onDelete}
              title="Delete cell"
              className="w-6 h-6 flex items-center justify-center rounded text-slate-600 hover:text-red-400 hover:bg-red-400/10 transition-colors"
            >
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path
                  d="M2 2L10 10M10 2L2 10"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="pl-[3px]" onKeyDown={handleKeyDown}>
        <Editor
          height={`${editorHeight}px`}
          language={language.monaco}
          value={cell.code}
          onChange={(val) => onCodeChange(val ?? "")}
          theme="vs-dark"
          options={EDITOR_OPTIONS}
          onMount={(editor, monaco) => {
            // Override background to match our palette
            monaco.editor.defineTheme("runcell", {
              base: "vs-dark",
              inherit: true,
              rules: [
                { token: "comment", foreground: "4a5568", fontStyle: "italic" },
              ],
              colors: {
                "editor.background": "#1A1D27",
                "editor.foreground": "#E2E8F0",
                "editorCursor.foreground": "#7C6AF7",
                "editor.selectionBackground": "#7C6AF720",
                "editor.lineHighlightBackground": "#00000000",
                "editorLineNumber.foreground": "#3A3D50",
                "editorLineNumber.activeForeground": "#7C6AF7",
                "editor.inactiveSelectionBackground": "#7C6AF710",
              },
            });
            monaco.editor.setTheme("runcell");
            // Resize editor on content change
            editor.onDidChangeModelContent(() => {
              const lines = editor.getModel()?.getLineCount() ?? 1;
              const newH = Math.min(Math.max(lines * 22 + 30, 120), 480);
              editor.layout({
                height: newH,
                width: editor.getLayoutInfo().width,
              });
            });
          }}
        />
      </div>

      {/* Run Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 border-t border-[#2A2D3E]/60">
        <span className="text-[10px] text-slate-600 font-mono">
          {cell.status === "running" ? "executing…" : "⌘ + Enter to run"}
        </span>
        <RunButton status={cell.status} onClick={onRun} />
      </div>

      {/* Output */}
      {cell.output !== null && (
        <OutputPane output={cell.output} status={cell.status} />
      )}

      {/* Add cell below */}
      <div className="flex justify-center pb-1 pt-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <button
          onClick={onAddAfter}
          className="flex items-center gap-1.5 text-[10px] text-slate-600 hover:text-[#7C6AF7] transition-colors px-3 py-1 rounded-full hover:bg-[#7C6AF7]/10"
        >
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path
              d="M5 1V9M1 5H9"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
          Add cell
        </button>
      </div>
    </div>
  );
}
