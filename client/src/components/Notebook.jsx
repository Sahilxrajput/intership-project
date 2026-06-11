import { useState, useEffect, useRef } from "react";
import Cell from "./Cell";

let cellIdCounter = 1;

const createCell = (code = "") => ({
  id: cellIdCounter++,
  code,
  output: null,
  status: "idle", // idle | running | success | error
});

export default function Notebook({ language, defaultCode }) {
  const [cells, setCells] = useState([createCell(defaultCode)]);
  const bottomRef = useRef(null);

  // Reset cells when language changes
  useEffect(() => {
    setCells([createCell(defaultCode)]);
  }, [language]);

  const updateCell = (id, patch) => {
    setCells((prev) => prev.map((c) => (c.id === id ? { ...c, ...patch } : c)));
  };

  const runCell = async (id) => {
    const cell = cells.find((c) => c.id === id);
    if (!cell) return;

    updateCell(id, { status: "running", output: null });

    try {
      const result = await executeCode(cell.code, language);
      updateCell(id, {
        status: result.error ? "error" : "success",
        output: result,
      });
    } catch (e) {
      updateCell(id, {
        status: "error",
        output: { error: true, text: e.message },
      });
    }
  };

  const addCellAfter = (id) => {
    setCells((prev) => {
      const idx = prev.findIndex((c) => c.id === id);
      const newCell = createCell("");
      const next = [...prev];
      next.splice(idx + 1, 0, newCell);
      return next;
    });
    // Scroll to bottom after render
    setTimeout(
      () => bottomRef.current?.scrollIntoView({ behavior: "smooth" }),
      50,
    );
  };

  // Run last cell on Ctrl+Enter / Cmd+Enter
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        const last = cells[cells.length - 1];
        if (last) runCell(last.id);
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [cells]);

  const deleteCell = (id) => {
    setCells((prev) =>
      prev.length > 1 ? prev.filter((c) => c.id !== id) : prev,
    );
  };

  return (
    <div className="flex flex-col gap-3">
      {cells.map((cell, idx) => (
        <Cell
          key={cell.id}
          cell={cell}
          index={idx}
          language={language}
          onCodeChange={(code) => updateCell(cell.id, { code })}
          onRun={() => runCell(cell.id)}
          onAddAfter={() => addCellAfter(cell.id)}
          onDelete={() => deleteCell(cell.id)}
          canDelete={cells.length > 1}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

// ─── Execution engine ───────────────────────────────────────────────────────

async function executeCode(code, language) {
  if (language === "javascript") {
    return runJS(code);
  }
  // For Python, Java, C++ — we call Judge0-compatible demo or show a notice
  return runViaAPI(code, language);
}

function runJS(code) {
  const logs = [];
  const originalLog = console.log;
  const originalError = console.error;
  const originalWarn = console.warn;

  const capture = (...args) =>
    logs.push(
      args
        .map((a) =>
          typeof a === "object" ? JSON.stringify(a, null, 2) : String(a),
        )
        .join(" "),
    );

  console.log = capture;
  console.error = (...args) => {
    capture(...args);
  };
  console.warn = capture;

  try {
    // eslint-disable-next-line no-new-func
    const fn = new Function(code);
    const result = fn();
    if (result !== undefined && logs.length === 0) logs.push(String(result));
    console.log = originalLog;
    console.error = originalError;
    console.warn = originalWarn;
    return { error: false, text: logs.join("\n") || "(no output)" };
  } catch (e) {
    console.log = originalLog;
    console.error = originalError;
    console.warn = originalWarn;
    return { error: true, text: e.toString() };
  }
}

async function runViaAPI(code, language) {
  try {
    const submitRes = await fetch(import.meta.env.VITE_API_URL+"/execute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ language, code }),
    });

    
    if (!submitRes.ok) throw new Error("Execution service unavailable.");
    const data = await submitRes.json();
    console.log("data: ", data);

    const out = data.stdout || "";
    const err = data.stderr || data.compile_output || "";
    const isErr = !!err && !out;

    return {
      error: isErr,
      text: isErr ? err.trim() : out.trim() || "(no output)",
      ...(err && out ? { stderr: err.trim() } : {}),
    };
  } catch (e) {
    // Graceful fallback — show a note rather than crash
    return {
      error: false,
      simulated: true,
      text: getSimulatedOutput(code, language),
      note: "Live execution requires a Judge0 API key. Showing simulated output.",
    };
  }
}

function getSimulatedOutput(code, language) {
  const printPatterns = {
    python: /print\(["'`]?(.*?)["'`]?\)/g,
    cpp: /cout\s*<<\s*["']?(.*?)["']?\s*(?:<<\s*endl|;)/g,
    java: /System\.out\.println\(["']?(.*?)["']?\)/g,
  };

  const pattern = printPatterns[language];
  if (!pattern) return "(no output)";

  const matches = [...code.matchAll(pattern)].map((m) => m[1].trim());
  return matches.length > 0 ? matches.join("\n") : "(no output)";
}
