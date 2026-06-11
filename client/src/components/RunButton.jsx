export default function RunButton({ status, onClick }) {
  const isRunning = status === "running";

  return (
    <button
      onClick={onClick}
      disabled={isRunning}
      className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
        isRunning
          ? "bg-[#7C6AF7]/20 text-[#7C6AF7] cursor-not-allowed"
          : "bg-[#7C6AF7] hover:bg-[#9183F8] text-white shadow-sm hover:shadow-[0_0_12px_rgba(124,106,247,0.35)] active:scale-95"
      }`}
    >
      {isRunning ? (
        <>
          <svg
            className="animate-spin"
            width="12"
            height="12"
            viewBox="0 0 12 12"
            fill="none"
          >
            <circle cx="6" cy="6" r="4.5" stroke="currentColor" strokeWidth="1.5" strokeDasharray="14 28" />
          </svg>
          Running
        </>
      ) : (
        <>
          <svg width="10" height="12" viewBox="0 0 10 12" fill="none">
            <path d="M1 1.5L9 6L1 10.5V1.5Z" fill="currentColor" />
          </svg>
          Run
        </>
      )}
    </button>
  );
}
