import { useState } from "react";
import Editor from "@monaco-editor/react";

import {
  FileCode2,
  Folder,
  ChevronDown,
  Play,
  Bug,
  ShieldCheck,
  Zap,
  Lightbulb,
  CheckCircle2
} from "lucide-react";

import "./CodeAnalyzer.css";

const API_URL = import.meta.env.VITE_API_URL;

function CodeAnalyzer() {
  const [code, setCode] = useState(
`def calculate_average(numbers):

    total = 0

    for number in numbers:
        total = total + number

    average = total / len(numbers)

    return average
`
  );

  const [activeTab, setActiveTab] = useState("Summary");
  const [analyzed, setAnalyzed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [analysis, setAnalysis] = useState({
    health: 0,
    bugs: 0,
    security: 0,
    time_complexity: "Unknown",
    space_complexity: "Unknown",
    bug_details: [],
    security_details: [],
    suggestions: []
  });

  const runAnalysis = async () => {
    if (!code.trim()) {
      setError("Please enter some code first.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalyzed(false);

    try {
      const response = await fetch(`${API_URL}/analyze-code`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        body: JSON.stringify({
          code: code,
          language: "python"
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Code analysis failed"
        );
      }

      setAnalysis({
        health: data.health ?? 0,
        bugs: data.bugs ?? 0,
        security: data.security ?? 0,
        time_complexity: data.time_complexity ?? "Unknown",
        space_complexity: data.space_complexity ?? "Unknown",
        bug_details: data.bug_details ?? [],
        security_details: data.security_details ?? [],
        suggestions: data.suggestions ?? []
      });

      setAnalyzed(true);
      setActiveTab("Summary");

    } catch (error) {
      console.error("Code Analysis Error:", error);

      setError(
        "Unable to connect to CodeGuard backend."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analyzer-workspace">

      {/* FILE EXPLORER */}

      <aside className="file-panel">

        <div className="file-header">
          <span>EXPLORER</span>
          <span className="file-count">3</span>
        </div>

        <div className="project-name">
          <ChevronDown size={14} />
          <Folder size={15} />
          <span>codeguard-project</span>
        </div>

        <div className="file-list">

          <div className="file-item active">
            <FileCode2 size={15} />
            <span>main.py</span>
          </div>

          <div className="file-item">
            <FileCode2 size={15} />
            <span>utils.py</span>
          </div>

          <div className="file-item">
            <FileCode2 size={15} />
            <span>requirements.txt</span>
          </div>

        </div>

        <div className="file-bottom">
          <span>PYTHON PROJECT</span>
          <span>3 FILES</span>
        </div>

      </aside>


      {/* CODE EDITOR */}

      <section className="editor-section">

        <div className="editor-header">

          <div className="editor-file">
            <FileCode2 size={15} />
            <span>main.py</span>
            <span className="modified">●</span>
          </div>

          <button
            className="run-button"
            onClick={runAnalysis}
            disabled={loading}
          >

            <Play size={14} />

            {loading ? "Analyzing..." : "Analyze Code"}

          </button>

        </div>

        <div className="monaco-container">

          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={(value) => setCode(value || "")}
            theme="vs-dark"
            options={{
              minimap: {
                enabled: false
              },

              fontSize: 13,

              padding: {
                top: 18
              },

              automaticLayout: true,

              scrollBeyondLastLine: false,

              smoothScrolling: true,

              cursorBlinking: "smooth",

              lineNumbers: "on"
            }}
          />

        </div>

        <div className="editor-status">
          <span>Python</span>
          <span>UTF-8</span>
          <span>LF</span>

          <span className="status-ready">
            ● {loading ? "Analyzing..." : "Ready"}
          </span>
        </div>

      </section>


      {/* ANALYSIS PANEL */}

      <aside className="analysis-panel">

        <div className="analysis-header">

          <div>
            <strong>Code Analysis</strong>

            <span>
              AI-powered inspection
            </span>
          </div>

          <div className="analysis-status">
            <span></span>
            {loading ? "ANALYZING" : "READY"}
          </div>

        </div>


        {/* TABS */}

        <div className="analysis-tabs">

          <button
            className={
              activeTab === "Summary"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("Summary")}
          >
            Summary
          </button>

          <button
            className={
              activeTab === "Bugs"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("Bugs")}
          >
            Bugs
          </button>

          <button
            className={
              activeTab === "Complexity"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("Complexity")}
          >
            Complexity
          </button>

          <button
            className={
              activeTab === "Security"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("Security")}
          >
            Security
          </button>

          <button
            className={
              activeTab === "Suggestions"
                ? "tab active"
                : "tab"
            }
            onClick={() => setActiveTab("Suggestions")}
          >
            Suggestions
          </button>

        </div>


        <div className="analysis-content">

          {error && (
            <div className="analysis-empty">

              <div className="empty-icon">
                <Bug size={20} />
              </div>

              <strong>
                Analysis failed
              </strong>

              <p>
                {error}
              </p>

              <button onClick={runAnalysis}>
                Try Again
              </button>

            </div>
          )}


          {!analyzed && !error && (

            <div className="analysis-empty">

              <div className="empty-icon">
                <Zap size={20} />
              </div>

              <strong>
                Ready to analyze
              </strong>

              <p>
                Run CodeGuard analysis to detect
                bugs, complexity and security issues.
              </p>

              <button onClick={runAnalysis}>
                Analyze Code
              </button>

            </div>
          )}


          {/* SUMMARY */}

          {analyzed && activeTab === "Summary" && (

            <div className="summary-content">

              <div className="health-card">

                <div>
                  <span>CODE HEALTH</span>

                  <strong>
                    {analysis.health}
                  </strong>
                </div>

                <div className="health-circle">
                  {analysis.health}%
                </div>

              </div>


              <div className="issue-grid">

                <div className="issue-card">
                  <Bug size={17} />

                  <strong>
                    {analysis.bugs}
                  </strong>

                  <span>Bugs</span>
                </div>


                <div className="issue-card">
                  <ShieldCheck size={17} />

                  <strong>
                    {analysis.security}
                  </strong>

                  <span>Security</span>
                </div>


                <div className="issue-card">
                  <Zap size={17} />

                  <strong>
                    {analysis.time_complexity}
                  </strong>

                  <span>Complexity</span>
                </div>

              </div>


              <div className="success-message">

                <CheckCircle2 size={17} />

                <div>

                  <strong>
                    {analysis.bugs === 0
                      ? "No critical issues found"
                      : `${analysis.bugs} issue(s) found`}
                  </strong>

                  <span>
                    CodeGuard analysis completed successfully.
                  </span>

                </div>

              </div>

            </div>
          )}


          {/* BUGS */}

          {analyzed && activeTab === "Bugs" && (

            <div className="result-section">

              <div className="result-title">
                <Bug size={18} />
                Bug Detection
              </div>

              {analysis.bug_details.length === 0 ? (

                <div className="result-good">

                  <CheckCircle2 size={18} />

                  <div>

                    <strong>
                      No bugs detected
                    </strong>

                    <span>
                      Static analysis found no obvious
                      issues in this code.
                    </span>

                  </div>

                </div>

              ) : (

                analysis.bug_details.map(
                  (bug, index) => (

                    <div
                      className="suggestion"
                      key={index}
                    >
                      <strong>
                        {bug.title}
                      </strong>

                      <span>
                        {bug.description}
                      </span>
                    </div>

                  )
                )

              )}

            </div>
          )}


          {/* COMPLEXITY */}

          {analyzed && activeTab === "Complexity" && (

            <div className="result-section">

              <div className="result-title">
                <Zap size={18} />
                Complexity Analysis
              </div>

              <div className="complexity-box">

                <span>
                  TIME COMPLEXITY
                </span>

                <strong>
                  {analysis.time_complexity}
                </strong>

              </div>

              <div className="complexity-box">

                <span>
                  SPACE COMPLEXITY
                </span>

                <strong>
                  {analysis.space_complexity}
                </strong>

              </div>

            </div>
          )}


          {/* SECURITY */}

          {analyzed && activeTab === "Security" && (

            <div className="result-section">

              <div className="result-title">

                <ShieldCheck size={18} />

                Security Scan

              </div>

              {analysis.security_details.length === 0 ? (

                <div className="result-good">

                  <CheckCircle2 size={18} />

                  <div>

                    <strong>
                      No security issues detected
                    </strong>

                    <span>
                      No obvious vulnerable patterns
                      were found.
                    </span>

                  </div>

                </div>

              ) : (

                analysis.security_details.map(
                  (issue, index) => (

                    <div
                      className="suggestion"
                      key={index}
                    >

                      <strong>
                        {issue.title}
                      </strong>

                      <span>
                        {issue.description}
                      </span>

                    </div>

                  )
                )

              )}

            </div>
          )}


          {/* SUGGESTIONS */}

          {analyzed && activeTab === "Suggestions" && (

            <div className="result-section">

              <div className="result-title">

                <Lightbulb size={18} />

                Suggestions

              </div>

              {analysis.suggestions.map(
                (suggestion, index) => (

                  <div
                    className="suggestion"
                    key={index}
                  >

                    <strong>
                      {suggestion.title}
                    </strong>

                    <span>
                      {suggestion.description}
                    </span>

                  </div>

                )
              )}

            </div>
          )}

        </div>

      </aside>

    </div>
  );
}

export default CodeAnalyzer;