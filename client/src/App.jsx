import { useState } from "react";
import Notebook from "./components/Notebook";
import TopBar from "./components/TopBar";

// const LANGUAGES = [
//   { id: "javascript", label: "JS", full: "JavaScript", monaco: "javascript" },
//   { id: "python", label: "PY", full: "Python", monaco: "python" },
//   { id: "cpp", label: "C++", full: "C++", monaco: "cpp" },
//   { id: "java", label: "Java", full: "Java", monaco: "java" },
// ];

const LANGUAGES =['javascript', 'java', 'python', 'cpp']

const DEFAULT_CODE = {
  javascript: `// JavaScript\nconsole.log("Hello, World!");\n\nconst sum = (a, b) => a + b;\nconsole.log("Sum:", sum(3, 7));`,
  python: `# Python\nprint("Hello, World!")\n\ndef sum(a, b):\n    return a + b\n\nprint("Sum:", sum(3, 7))`,
  cpp: `// C++\n#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}`,
  java: `// Java\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}`,
};

export default function App() {
  const [language, setLanguage] = useState(LANGUAGES[0]);

  return (
    <div className="min-h-screen bg-[#0F1117] text-slate-200 font-sans">
      <TopBar languages={LANGUAGES} selected={language} onSelect={setLanguage} />
      <main className="max-w-screen mx-auto p-8">
        <Notebook language={language} defaultCode={DEFAULT_CODE[language]} />
      </main>
    </div>
  );
}
