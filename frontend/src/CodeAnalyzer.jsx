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


  const runAnalysis = () => {

    setAnalyzed(true);

    setActiveTab("Summary");

  };


  return (

    <div className="analyzer-workspace">


      {/* ================= FILE EXPLORER ================= */}

      <aside className="file-panel">

        <div className="file-header">

          <span>
            EXPLORER
          </span>

          <span className="file-count">
            3
          </span>

        </div>


        <div className="project-name">

          <ChevronDown size={14} />

          <Folder size={15} />

          <span>
            codeguard-project
          </span>

        </div>


        <div className="file-list">


          <div className="file-item active">

            <FileCode2 size={15} />

            <span>
              main.py
            </span>

          </div>


          <div className="file-item">

            <FileCode2 size={15} />

            <span>
              utils.py
            </span>

          </div>


          <div className="file-item">

            <FileCode2 size={15} />

            <span>
              requirements.txt
            </span>

          </div>


        </div>


        <div className="file-bottom">

          <span>
            PYTHON PROJECT
          </span>

          <span>
            3 FILES
          </span>

        </div>

      </aside>



      {/* ================= CODE EDITOR ================= */}

      <section className="editor-section">


        <div className="editor-header">


          <div className="editor-file">

            <FileCode2 size={15} />

            <span>
              main.py
            </span>

            <span className="modified">
              ●
            </span>

          </div>


          <button
            className="run-button"
            onClick={runAnalysis}
          >

            <Play size={14} />

            Analyze Code

          </button>


        </div>


        <div className="monaco-container">

          <Editor

            height="100%"

            defaultLanguage="python"

            value={code}

            onChange={(value) =>
              setCode(value || "")
            }

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

          <span>
            Python
          </span>

          <span>
            UTF-8
          </span>

          <span>
            LF
          </span>

          <span className="status-ready">
            ● Ready
          </span>

        </div>

      </section>



      {/* ================= ANALYSIS PANEL ================= */}

      <aside className="analysis-panel">


        <div className="analysis-header">

          <div>

            <strong>
              Code Analysis
            </strong>

            <span>
              AI-powered inspection
            </span>

          </div>


          <div className="analysis-status">

            <span></span>

            READY

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

            onClick={() =>
              setActiveTab("Summary")
            }
          >
            Summary
          </button>


          <button
            className={
              activeTab === "Bugs"
                ? "tab active"
                : "tab"
            }

            onClick={() =>
              setActiveTab("Bugs")
            }
          >
            Bugs
          </button>


          <button
            className={
              activeTab === "Complexity"
                ? "tab active"
                : "tab"
            }

            onClick={() =>
              setActiveTab("Complexity")
            }
          >
            Complexity
          </button>


          <button
            className={
              activeTab === "Security"
                ? "tab active"
                : "tab"
            }

            onClick={() =>
              setActiveTab("Security")
            }
          >
            Security
          </button>


          <button
            className={
              activeTab === "Suggestions"
                ? "tab active"
                : "tab"
            }

            onClick={() =>
              setActiveTab("Suggestions")
            }
          >
            Suggestions
          </button>


        </div>



        {/* ================= TAB CONTENT ================= */}

        <div className="analysis-content">


          {!analyzed && (

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

              <button
                onClick={runAnalysis}
              >
                Analyze Code
              </button>

            </div>

          )}



          {analyzed && activeTab === "Summary" && (

            <div className="summary-content">


              <div className="health-card">

                <div>

                  <span>
                    CODE HEALTH
                  </span>

                  <strong>
                    92
                  </strong>

                </div>

                <div className="health-circle">
                  92%
                </div>

              </div>


              <div className="issue-grid">


                <div className="issue-card">

                  <Bug size={17} />

                  <strong>
                    0
                  </strong>

                  <span>
                    Bugs
                  </span>

                </div>


                <div className="issue-card">

                  <ShieldCheck size={17} />

                  <strong>
                    0
                  </strong>

                  <span>
                    Security
                  </span>

                </div>


                <div className="issue-card">

                  <Zap size={17} />

                  <strong>
                    O(n)
                  </strong>

                  <span>
                    Complexity
                  </span>

                </div>


              </div>


              <div className="success-message">

                <CheckCircle2 size={17} />

                <div>

                  <strong>
                    No critical issues found
                  </strong>

                  <span>
                    Your code looks clean.
                  </span>

                </div>

              </div>


            </div>

          )}



          {analyzed && activeTab === "Bugs" && (

            <div className="result-section">

              <div className="result-title">

                <Bug size={18} />

                Bug Detection

              </div>


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

            </div>

          )}



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
                  O(n)
                </strong>

              </div>


              <div className="complexity-box">

                <span>
                  SPACE COMPLEXITY
                </span>

                <strong>
                  O(1)
                </strong>

              </div>

            </div>

          )}



          {analyzed && activeTab === "Security" && (

            <div className="result-section">

              <div className="result-title">

                <ShieldCheck size={18} />

                Security Scan

              </div>


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

            </div>

          )}



          {analyzed && activeTab === "Suggestions" && (

            <div className="result-section">

              <div className="result-title">

                <Lightbulb size={18} />

                Suggestions

              </div>


              <div className="suggestion">

                <strong>
                  Improve variable naming
                </strong>

                <span>
                  Use descriptive names for better
                  readability.
                </span>

              </div>


              <div className="suggestion">

                <strong>
                  Add input validation
                </strong>

                <span>
                  Handle empty lists before calculating
                  the average.
                </span>

              </div>

            </div>

          )}


        </div>


      </aside>


    </div>

  );

}


export default CodeAnalyzer;