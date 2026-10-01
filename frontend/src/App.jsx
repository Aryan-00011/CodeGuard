import Auth from "./Auth";

import { useEffect, useRef, useState } from "react";

import {
  Plus,
  Search,
  Settings,
  User,
  Paperclip,
  Send,
  Bug,
  Zap,
  RefreshCw,
  FlaskConical,
  Copy,
  Check,
  MoreHorizontal,
  Trash2,
  X,
  Sparkles,
  LogOut
} from "lucide-react";

import "./App.css";


// =====================================================
// PRODUCTION BACKEND URL
// =====================================================
const API_URL = import.meta.env.VITE_API_URL;

// =====================================================
// MAIN APP
// =====================================================

function App() {

  const [user, setUser] = useState(() => {

    const savedUser =
      localStorage.getItem("codeguard_user");

    if (!savedUser) {
      return null;
    }

    try {

      return JSON.parse(savedUser);

    } catch (error) {

      console.error(
        "User load error:",
        error
      );

      return null;

    }

  });


  // =====================================================
  // LOGIN
  // =====================================================

  const handleLogin = (loggedInUser) => {

    localStorage.setItem(
      "codeguard_user",
      JSON.stringify(loggedInUser)
    );

    setUser(loggedInUser);

  };


  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {

    localStorage.removeItem(
      "codeguard_user"
    );

    setUser(null);

  };


  // =====================================================
  // AUTH SCREEN
  // =====================================================

  if (!user) {

    return (
      <Auth
        onLogin={handleLogin}
      />
    );

  }


  // =====================================================
  // CODEGUARD APP
  // =====================================================

  return (
    <CodeGuardApp
      user={user}
      onLogout={handleLogout}
    />
  );

}


// =====================================================
// CODEGUARD APP
// =====================================================

function CodeGuardApp({
  user,
  onLogout
}) {

  // =====================================================
  // STATES
  // =====================================================

  const [message, setMessage] =
    useState("");

  const [messages, setMessages] =
    useState([]);

  const [language, setLanguage] =
    useState("Python");

  const [loading, setLoading] =
    useState(false);

  const [copied, setCopied] =
    useState(false);

  const [chats, setChats] =
    useState([]);

  const [currentChatId, setCurrentChatId] =
    useState(null);

  const [searchText, setSearchText] =
    useState("");

  const [searchOpen, setSearchOpen] =
    useState(false);

  const [profileOpen, setProfileOpen] =
    useState(false);

  const [settingsOpen, setSettingsOpen] =
    useState(false);

  const [darkMode, setDarkMode] =
    useState(true);

  const [theme, setTheme] =
    useState(
      localStorage.getItem(
        "codeguard_theme"
      ) || "dark"
    );

  const [menuChatId, setMenuChatId] =
    useState(null);


  // =====================================================
  // FILE UPLOAD
  // =====================================================

  const fileInputRef =
    useRef(null);

  const [attachedFile, setAttachedFile] =
    useState(null);


  // =====================================================
  // SUPPORTED LANGUAGES
  // =====================================================

  const supportedLanguages = [
    "Python",
    "Java",
    "C++",
    "C",
    "JavaScript",
    "TypeScript",
    "C#"
  ];


  // =====================================================
  // LOAD CHAT HISTORY
  // =====================================================

  useEffect(() => {

    const savedChats =
      localStorage.getItem(
        "codeguard_chats"
      );

    if (!savedChats) {
      return;
    }

    try {

      const parsedChats =
        JSON.parse(savedChats);

      if (Array.isArray(parsedChats)) {

        setChats(parsedChats);

      }

    } catch (error) {

      console.error(
        "History load error:",
        error
      );

    }

  }, []);


  // =====================================================
  // SAVE CHAT HISTORY
  // =====================================================

  useEffect(() => {

    localStorage.setItem(
      "codeguard_chats",
      JSON.stringify(chats)
    );

  }, [chats]);


  // =====================================================
  // SAVE THEME
  // =====================================================

  useEffect(() => {

    localStorage.setItem(
      "codeguard_theme",
      theme
    );

    if (theme === "light") {

      setDarkMode(false);

    } else {

      setDarkMode(true);

    }

  }, [theme]);


  // =====================================================
  // DARK MODE
  // =====================================================

  const handleDarkModeChange = (
    enabled
  ) => {

    setDarkMode(enabled);

    if (enabled) {

      setTheme("dark");

    } else {

      setTheme("light");

    }

  };


  // =====================================================
  // COPY CODE
  // =====================================================

  const copyCode = async (
    code
  ) => {

    try {

      await navigator.clipboard.writeText(
        code
      );

      setCopied(true);

      setTimeout(() => {

        setCopied(false);

      }, 2000);

    } catch (error) {

      console.error(
        "Copy error:",
        error
      );

    }

  };


  // =====================================================
  // FILE UPLOAD
  // =====================================================

  const handleFileUpload = (
    event
  ) => {

    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }


    const extension =
      file.name
        .split(".")
        .pop()
        .toLowerCase();


    const languageMap = {

      py: "Python",
      python: "Python",
      java: "Java",
      cpp: "C++",
      cc: "C++",
      cxx: "C++",
      c: "C",
      js: "JavaScript",
      jsx: "JavaScript",
      ts: "TypeScript",
      tsx: "TypeScript",
      cs: "C#"

    };


    const detectedLanguage =
      languageMap[extension];


    if (detectedLanguage) {

      setLanguage(
        detectedLanguage
      );

    }


    setAttachedFile(file);


    const reader =
      new FileReader();


    reader.onload = (e) => {

      const fileContent =
        e.target?.result;

      if (
        typeof fileContent === "string"
      ) {

        setMessage(
          fileContent
        );

      }

    };


    reader.onerror = () => {

      alert(
        "Unable to read this file."
      );

      setAttachedFile(null);

    };


    reader.readAsText(file);

    event.target.value = "";

  };


  // =====================================================
  // REMOVE FILE
  // =====================================================

  const removeAttachedFile = () => {

    setAttachedFile(null);

    setMessage("");

  };


  // =====================================================
  // CREATE CHAT ID
  // =====================================================

  const createChatId = () => {

    return (
      Date.now().toString() +
      Math.random()
        .toString(36)
        .substring(2, 8)
    );

  };


  // =====================================================
  // CHAT TITLE
  // =====================================================

  const getChatTitle = (
    chatMessages
  ) => {

    if (
      !chatMessages ||
      chatMessages.length === 0
    ) {

      return "New Chat";

    }


    const firstUserMessage =
      chatMessages.find(
        (item) =>
          item.role === "user"
      );


    if (!firstUserMessage) {

      return "New Chat";

    }


    let title =
      firstUserMessage.text
        .replace(/\n/g, " ")
        .trim();


    if (title.length > 35) {

      title =
        title.substring(0, 35) +
        "...";

    }


    return title || "New Chat";

  };


  // =====================================================
  // SAVE CHAT
  // =====================================================

  const saveChat = (
    updatedMessages,
    chatId
  ) => {

    if (
      !updatedMessages ||
      updatedMessages.length === 0
    ) {

      return chatId;

    }


    let id = chatId;


    if (!id) {

      id =
        createChatId();

    }


    setCurrentChatId(id);


    setChats(
      (previousChats) => {

        const existingChat =
          previousChats.find(
            (chat) =>
              chat.id === id
          );


        if (existingChat) {

          return previousChats.map(
            (chat) => {

              if (
                chat.id === id
              ) {

                return {

                  ...chat,

                  title:
                    getChatTitle(
                      updatedMessages
                    ),

                  messages:
                    updatedMessages,

                  updatedAt:
                    new Date().toISOString()

                };

              }


              return chat;

            }
          );

        }


        const newChat = {

          id: id,

          title:
            getChatTitle(
              updatedMessages
            ),

          messages:
            updatedMessages,

          updatedAt:
            new Date().toISOString()

        };


        return [
          newChat,
          ...previousChats
        ];

      }
    );


    return id;

  };


  // =====================================================
  // NEW CHAT
  // =====================================================

  const createNewChat = () => {

    setMessages([]);

    setCurrentChatId(null);

    setMessage("");

    setAttachedFile(null);

    setMenuChatId(null);

    setSearchText("");

  };


  // =====================================================
  // ADD USER MESSAGE
  // =====================================================

  const addUserMessage = (
    text
  ) => {

    const updatedMessages = [

      ...messages,

      {
        role: "user",
        text: text
      }

    ];


    setMessages(
      updatedMessages
    );


    const chatId =
      saveChat(
        updatedMessages,
        currentChatId
      );


    return {

      messages:
        updatedMessages,

      chatId:
        chatId

    };

  };


  // =====================================================
  // ADD ASSISTANT MESSAGE
  // =====================================================

  const addAssistantMessage = (
    assistantMessage,
    baseMessages,
    chatId
  ) => {

    const updatedMessages = [

      ...(baseMessages || []),

      assistantMessage

    ];


    setMessages(
      updatedMessages
    );


    saveChat(
      updatedMessages,
      chatId
    );

  };


  // =====================================================
  // BUG RESULT
  // =====================================================

  const createBugResult = (
    analysis
  ) => {

    let result =
      "🐞 Bug Analysis\n\n";


    if (
      analysis.syntax &&
      !analysis.syntax.valid
    ) {

      result +=
        "❌ Syntax Error\n\n";


      if (
        analysis.syntax.error
      ) {

        if (
          typeof analysis.syntax.error ===
          "object"
        ) {

          result +=
            `Line: ${
              analysis.syntax.error.line ||
              "Unknown"
            }\n`;

          result +=
            `Column: ${
              analysis.syntax.error.column ||
              "Unknown"
            }\n`;

          result +=
            `Message: ${
              analysis.syntax.error.message ||
              "Syntax error"
            }\n\n`;

        } else {

          result +=
            `Message: ${
              analysis.syntax.error
            }\n\n`;

        }

      }

    } else {

      result +=
        "✅ Syntax: No syntax errors found.\n\n";

    }


    if (
      analysis.bugs &&
      analysis.bugs.length > 0
    ) {

      result +=
        `❌ ${
          analysis.bugs.length
        } potential issue(s) found\n\n`;


      analysis.bugs.forEach(
        (bug) => {

          result +=
            `• ${
              bug.message
            }\n`;


          if (bug.variable) {

            result +=
              `  Variable: ${
                bug.variable
              }\n`;

          }


          if (bug.line) {

            result +=
              `  Line: ${
                bug.line
              }\n`;

          }


          if (bug.suggestion) {

            result +=
              `  Suggestion: ${
                bug.suggestion
              }\n`;

          }


          result += "\n";

        }
      );

    } else {

      result +=
        "🟢 No obvious bugs detected.\n";

    }


    return result;

  };


  // =====================================================
  // COMPLEXITY RESULT
  // =====================================================

  const createComplexityResult = (
    analysis
  ) => {

    let result =
      "⚡ Complexity Analysis\n\n";


    if (
      analysis.complexity
    ) {

      result +=
        `Time Complexity: ${
          analysis.complexity.time
        }\n`;

      result +=
        `Space Complexity: ${
          analysis.complexity.space
        }\n\n`;


      if (
        analysis.complexity.reason
      ) {

        result +=
          `Reason: ${
            analysis.complexity.reason
          }\n`;

      }


      if (
        analysis.complexity.space_reason
      ) {

        result +=
          `Space Reason: ${
            analysis.complexity.space_reason
          }\n`;

      }

    } else {

      result +=
        "Complexity analysis is not available.\n";

    }


    return result;

  };


  // =====================================================
  // SECURITY RESULT
  // =====================================================

  const createSecurityResult = (
    analysis
  ) => {

    let result =
      "🔐 Security Analysis\n\n";


    const security =
      analysis.security || [];


    if (
      security.length === 0
    ) {

      result +=
        "🟢 No security vulnerabilities detected.\n";

      return result;

    }


    result +=
      `⚠️ ${
        security.length
      } vulnerability(ies) found.\n\n`;


    security.forEach(
      (item) => {

        result +=
          `• ${
            item.type
          }\n`;


        if (
          item.severity
        ) {

          result +=
            `  Severity: ${
              item.severity
            }\n`;

        }


        if (
          item.line
        ) {

          result +=
            `  Line: ${
              item.line
            }\n`;

        }


        result +=
          `  ${
            item.message
          }\n`;


        if (
          item.suggestion
        ) {

          result +=
            `  Suggestion: ${
              item.suggestion
            }\n`;

        }


        result += "\n";

      }
    );


    return result;

  };


  // =====================================================
  // REFACTOR RESULT
  // =====================================================

  const createRefactorResult = (
    analysis,
    originalCode
  ) => {

    let result =
      "🔄 Refactoring\n\n";


    const refactoring =
      analysis.refactoring;


    if (
      refactoring &&
      refactoring.suggestions &&
      refactoring.suggestions.length > 0
    ) {

      result +=
        `${
          refactoring.suggestions.length
        } improvement(s) found.\n\n`;


      refactoring.suggestions.forEach(
        (item) => {

          result +=
            `• ${
              item.type
            }\n`;


          if (
            item.line
          ) {

            result +=
              `  Line: ${
                item.line
              }\n`;

          }


          result +=
            `  ${
              item.message
            }\n`;


          if (
            item.suggestion
          ) {

            result +=
              `  Suggestion: ${
                item.suggestion
              }\n`;

          }


          result += "\n";

        }
      );

    } else {

      result +=
        "🟢 No obvious refactoring opportunities found.\n\n";

    }


    const refactoredCode =
      refactoring?.refactored_code;


    if (
      refactoredCode &&
      refactoredCode.trim() !==
      originalCode.trim()
    ) {

      result +=
        "✨ Refactored Code\n\n";

      result +=
        refactoredCode;

      result += "\n";

    }


    return {

      text:
        result,

      refactoredCode:
        refactoredCode &&
        refactoredCode.trim() !==
        originalCode.trim()
          ? refactoredCode
          : null

    };

  };


  // =====================================================
  // TEST RESULT
  // =====================================================

  const createTestResult = (
    analysis
  ) => {

    let result =
      "🧪 Test Cases\n\n";


    const testCases =
      analysis.test_cases?.test_cases ||
      [];


    if (
      testCases.length > 0
    ) {

      testCases.forEach(
        (testCase, index) => {

          result +=
            `• Test Case ${
              index + 1
            } — ${
              testCase.type
            }\n`;

          result +=
            `  ${
              testCase.description
            }\n`;

          result +=
            `  Input: ${
              testCase.input
            }\n`;

          result +=
            `  Expected: ${
              testCase.expected
            }\n\n`;

        }
      );

    } else {

      result +=
        `${
          analysis.test_cases?.message ||
          "No test cases generated."
        }\n\n`;

    }


    const execution =
      analysis.test_execution;


    if (
      execution &&
      execution.results &&
      execution.results.length > 0
    ) {

      result +=
        "▶ Test Execution\n\n";


      execution.results.forEach(
        (test) => {

          if (
            test.status === "PASS"
          ) {

            result +=
              `✅ Test Case ${
                test.test_case
              } — ${
                test.type
              }\n`;

            result +=
              `   Input: ${
                JSON.stringify(
                  test.input
                )
              }\n`;

            result +=
              `   Output: ${
                JSON.stringify(
                  test.output
                )
              }\n\n`;

          } else {

            result +=
              `❌ Test Case ${
                test.test_case
              } — ${
                test.type
              }\n`;

            result +=
              `   Input: ${
                JSON.stringify(
                  test.input
                )
              }\n`;

            result +=
              `   Error: ${
                test.error
              }\n\n`;

          }

        }
      );


      result +=
        `📊 Result: ${
          execution.passed
        }/${
          execution.total
        } Test Cases Passed\n`;

    } else if (
      execution?.message
    ) {

      result +=
        `▶ Test Execution\n\n${
          execution.message
        }\n`;

    }


    return result;

  };


  // =====================================================
  // FULL STATIC ANALYSIS
  // =====================================================

  const createFullResult = (
    analysis
  ) => {

    let result =
      "CodeGuard Analysis\n\n";


    if (
      analysis.syntax &&
      analysis.syntax.valid
    ) {

      result +=
        "🟢 Syntax: Valid\n";

    } else {

      result +=
        "🔴 Syntax: Error\n";

    }


    const bugs =
      analysis.bugs || [];


    result +=
      `🐞 Bugs: ${
        bugs.length
      }\n`;


    if (
      analysis.complexity
    ) {

      result +=
        `⚡ Time: ${
          analysis.complexity.time
        }\n`;

      result +=
        `⚡ Space: ${
          analysis.complexity.space
        }\n`;

    }


    const security =
      analysis.security || [];


    result +=
      `🔐 Security: ${
        security.length === 0
          ? "No issues"
          : `${security.length} issue(s)`
      }\n`;


    const refactoring =
      analysis.refactoring;


    const suggestions =
      refactoring?.suggestions || [];


    result +=
      `🔄 Refactoring: ${
        suggestions.length
      } suggestion(s)\n`;


    const execution =
      analysis.test_execution;


    if (
      execution &&
      execution.total > 0
    ) {

      result +=
        `🧪 Tests: ${
          execution.passed
        }/${
          execution.total
        } passed\n`;

    }


    return result;

  };


  // =====================================================
  // GET AI EXPLANATION
  // =====================================================

  const getAIExplanation = (
    reviewText
  ) => {

    if (!reviewText) {

      return "";

    }


    const codeSectionIndex =
      reviewText.search(
        /(?:Solution Code|Fixed Code|Improved Code):/i
      );


    if (
      codeSectionIndex === -1
    ) {

      return reviewText.trim();

    }


    return reviewText
      .substring(
        0,
        codeSectionIndex
      )
      .trim();

  };


  // =====================================================
  // DETECT LEETCODE / DSA
  // =====================================================

  const isLeetCodeResponse = (
    aiReview
  ) => {

    if (
      !aiReview ||
      !aiReview.success ||
      !aiReview.review
    ) {

      return false;

    }


    const reviewText =
      aiReview.review;


    return (

      /Mode:\s*LeetCode/i.test(
        reviewText
      )

      ||

      /Solution Code:/i.test(
        reviewText
      )

      ||

      /LeetCode/i.test(
        reviewText
      )

    );

  };


  // =====================================================
  // AI REVIEW RESULT
  // =====================================================

  const createAIReviewResult = (
    aiReview
  ) => {

    if (!aiReview) {

      return null;

    }


    if (
      !aiReview.success
    ) {

      return (
        "🤖 AI Fix\n\n" +

        "⚠️ AI review could not be completed.\n\n" +

        `Reason: ${
          aiReview.message ||
          "Unknown error"
        }`
      );

    }


    const explanation =
      getAIExplanation(
        aiReview.review
      );


    const title =
      isLeetCodeResponse(
        aiReview
      )
        ? "🧠 AI LeetCode Solution"
        : "🤖 AI Analysis";


    return (
      title +
      "\n\n" +
      explanation
    );

  };


  // =====================================================
  // EXTRACT AI SOLUTION / FIXED CODE
  // =====================================================

  const extractImprovedCode = (
    aiReview
  ) => {

    if (
      !aiReview ||
      !aiReview.success ||
      !aiReview.review
    ) {

      return null;

    }


    const reviewText =
      aiReview.review;


    const codeMatch =
      reviewText.match(
        /(?:Solution Code|Fixed Code|Improved Code):\s*([\s\S]*)/i
      );


    if (
      !codeMatch ||
      !codeMatch[1]
    ) {

      return null;

    }


    let codeSection =
      codeMatch[1].trim();


    const fencedMatch =
      codeSection.match(
        /```(?:[a-zA-Z0-9+#.-]+)?\s*([\s\S]*?)```/
      );


    if (
      fencedMatch &&
      fencedMatch[1]
    ) {

      codeSection =
        fencedMatch[1].trim();

    } else {

      codeSection =
        codeSection.replace(
          /^```[a-zA-Z0-9+#.-]*\s*/i,
          ""
        );


      codeSection =
        codeSection.replace(
          /```\s*$/i,
          ""
        );

    }


    const remainingFenceIndex =
      codeSection.indexOf("```");


    if (
      remainingFenceIndex !== -1
    ) {

      codeSection =
        codeSection.substring(
          0,
          remainingFenceIndex
        ).trim();

    }


    const lowerCode =
      codeSection.toLowerCase();


    if (
      lowerCode.includes(
        "no changes required"
      )
    ) {

      return null;

    }


    if (
      lowerCode.includes(
        "no changes needed"
      )
    ) {

      return null;

    }


    if (
      !codeSection.trim()
    ) {

      return null;

    }


    return codeSection.trim();

  };


  // =====================================================
  // AI BUG RESULT
  // =====================================================

  const createAIBugResult = (
    analysis,
    aiReview
  ) => {

    const staticResult =
      createBugResult(
        analysis
      );


    const aiResult =
      createAIReviewResult(
        aiReview
      );


    let finalText =
      staticResult;


    if (aiResult) {

      finalText +=
        "\n\n────────────────────────\n\n";

      finalText +=
        aiResult;

    }


    return finalText;

  };


  // =====================================================
  // ANALYZE CODE
  // =====================================================

  const analyzeCode = async (
    code,
    action = "full",
    baseMessages,
    chatId
  ) => {

    try {

      setLoading(true);


      // =================================================
      // PRODUCTION BACKEND REQUEST
      // =================================================

      const endpoint =
        `${API_URL}/analyze`;


      console.log(
        "CodeGuard API:",
        endpoint
      );


      const response =
        await fetch(
          endpoint,
          {

            method: "POST",

            headers: {

              "Content-Type":
                "application/json"

            },

            body:
              JSON.stringify({

                code:
                  code,

                language:
                  language,

                action:
                  action

              })

          }
        );


      console.log(
        "Backend HTTP Status:",
        response.status
      );


      if (
        !response.ok
      ) {

        let serverMessage =
          `Server returned ${response.status}`;

        try {

          const errorData =
            await response.json();

          if (
            errorData?.message
          ) {

            serverMessage =
              errorData.message;

          }

        } catch (error) {

          console.log(
            "No JSON error response from backend."
          );

        }


        throw new Error(
          serverMessage
        );

      }


      const data =
        await response.json();


      console.log(
        "CodeGuard Backend Response:",
        data
      );


      if (
        !data.success ||
        !data.analysis
      ) {

        addAssistantMessage(

          {

            role:
              "assistant",

            text:
              data.message ||
              "No analysis result received from backend."

          },

          baseMessages,

          chatId

        );

        return;

      }


      const analysis =
        data.analysis;


      // =================================================
      // BUGS
      // =================================================

      if (
        action === "bugs"
      ) {

        const finalText =
          createAIBugResult(
            analysis,
            data.ai_review
          );


        const improvedCode =
          extractImprovedCode(
            data.ai_review
          );


        addAssistantMessage(

          {

            role:
              "assistant",

            text:
              finalText,

            aiReview:
              data.ai_review,

            improvedCode:
              improvedCode

          },

          baseMessages,

          chatId

        );

        return;

      }


      // =================================================
      // COMPLEXITY
      // =================================================

      if (
        action === "complexity"
      ) {

        const result =
          createComplexityResult(
            analysis
          );


        addAssistantMessage(

          {

            role:
              "assistant",

            text:
              result

          },

          baseMessages,

          chatId

        );

        return;

      }


      // =================================================
      // SECURITY
      // =================================================

      if (
        action === "security"
      ) {

        const result =
          createSecurityResult(
            analysis
          );


        addAssistantMessage(

          {

            role:
              "assistant",

            text:
              result

          },

          baseMessages,

          chatId

        );

        return;

      }


      // =================================================
      // REFACTOR
      // =================================================

      if (
        action === "refactor"
      ) {

        const refactorResult =
          createRefactorResult(
            analysis,
            code
          );


        addAssistantMessage(

          {

            role:
              "assistant",

            text:
              refactorResult.text,

            refactoredCode:
              refactorResult.refactoredCode

          },

          baseMessages,

          chatId

        );

        return;

      }


      // =================================================
      // TESTS
      // =================================================

      if (
        action === "tests"
      ) {

        const result =
          createTestResult(
            analysis
          );


        addAssistantMessage(

          {

            role:
              "assistant",

            text:
              result

          },

          baseMessages,

          chatId

        );

        return;

      }


      // =================================================
      // FULL ANALYSIS
      // =================================================

      const staticResult =
        createFullResult(
          analysis
        );


      const aiResult =
        createAIReviewResult(
          data.ai_review
        );


      let finalText =
        staticResult;


      if (aiResult) {

        finalText +=
          "\n\n────────────────────────\n\n";

        finalText +=
          aiResult;

      }


      const improvedCode =
        extractImprovedCode(
          data.ai_review
        );


      addAssistantMessage(

        {

          role:
            "assistant",

          text:
            finalText,

          aiReview:
            data.ai_review,

          improvedCode:
            improvedCode

        },

        baseMessages,

        chatId

      );


    } catch (error) {

      console.error(
        "================================="
      );

      console.error(
        "CODEGUARD BACKEND ERROR"
      );

      console.error(
        "================================="
      );

      console.error(
        "API URL:",
        API_URL
      );

      console.error(
        "Endpoint:",
        `${API_URL}/analyze`
      );

      console.error(
        "Error:",
        error
      );


      addAssistantMessage(

        {

          role:
            "assistant",

          text:
            `❌ Unable to connect to CodeGuard backend.

Backend:
${API_URL}

Please check the browser console for the exact error.`

        },

        baseMessages,

        chatId

      );


    } finally {

      setLoading(false);

    }

  };


  // =====================================================
  // QUICK ACTION
  // =====================================================

  const handleQuickAction = async (
    action
  ) => {

    if (
      !message.trim()
    ) {

      const warningMessage = {

        role:
          "assistant",

        text:
          "⚠️ Please paste your code first."

      };


      setMessages(
        (previousMessages) => [

          ...previousMessages,

          warningMessage

        ]
      );

      return;

    }


    if (
      loading
    ) {

      return;

    }


    const code =
      message;


    const userResult =
      addUserMessage(
        code
      );


    setMessage("");

    setAttachedFile(null);


    await analyzeCode(

      code,

      action,

      userResult.messages,

      userResult.chatId

    );

  };


  // =====================================================
  // SEND
  // =====================================================

  const handleSend = async () => {

    if (
      !message.trim() ||
      loading
    ) {

      return;

    }


    const code =
      message;


    const userResult =
      addUserMessage(
        code
      );


    setMessage("");

    setAttachedFile(null);


    await analyzeCode(

      code,

      "full",

      userResult.messages,

      userResult.chatId

    );

  };


  // =====================================================
  // OPEN CHAT
  // =====================================================

  const openChat = (
    chat
  ) => {

    setCurrentChatId(
      chat.id
    );


    setMessages(
      chat.messages || []
    );


    setMessage("");

    setAttachedFile(null);

    setMenuChatId(null);

  };


  // =====================================================
  // DELETE CHAT
  // =====================================================

  const deleteChat = (
    chatId
  ) => {

    setChats(
      (previousChats) =>
        previousChats.filter(
          (chat) =>
            chat.id !== chatId
        )
    );


    if (
      currentChatId === chatId
    ) {

      setCurrentChatId(null);

      setMessages([]);

    }


    setMenuChatId(null);

  };


  // =====================================================
  // SEARCH
  // =====================================================

  const filteredChats =
    chats.filter(
      (chat) =>
        chat.title
          .toLowerCase()
          .includes(
            searchText.toLowerCase()
          )
    );


  // =====================================================
  // DATE GROUP
  // =====================================================

  const getDateGroup = (
    date
  ) => {

    const chatDate =
      new Date(date);

    const today =
      new Date();

    const yesterday =
      new Date();


    yesterday.setDate(
      today.getDate() - 1
    );


    if (
      chatDate.toDateString() ===
      today.toDateString()
    ) {

      return "Today";

    }


    if (
      chatDate.toDateString() ===
      yesterday.toDateString()
    ) {

      return "Yesterday";

    }


    return "Previous 7 Days";

  };


  // =====================================================
  // GROUP CHATS
  // =====================================================

  const todayChats =
    filteredChats.filter(
      (chat) =>
        getDateGroup(
          chat.updatedAt
        ) === "Today"
    );


  const yesterdayChats =
    filteredChats.filter(
      (chat) =>
        getDateGroup(
          chat.updatedAt
        ) === "Yesterday"
    );


  const previousChats =
    filteredChats.filter(
      (chat) =>
        getDateGroup(
          chat.updatedAt
        ) === "Previous 7 Days"
    );


  // =====================================================
  // CHAT LIST
  // =====================================================

  const renderChatList = (
    chatList
  ) => {

    return chatList.map(
      (chat) => (

        <div
          key={chat.id}
          style={{
            position:
              "relative"
          }}
        >

          <button
            className="history-item"
            onClick={() =>
              openChat(chat)
            }
            style={{
              width:
                "100%",
              paddingRight:
                "35px"
            }}
          >

            {chat.title}

          </button>


          <button
            className="history-menu-button"
            onClick={(event) => {

              event.stopPropagation();

              setMenuChatId(
                menuChatId === chat.id
                  ? null
                  : chat.id
              );

            }}
            style={{
              position:
                "absolute",
              right:
                "5px",
              top:
                "50%",
              transform:
                "translateY(-50%)",
              background:
                "none",
              border:
                "none",
              cursor:
                "pointer",
              color:
                "inherit"
            }}
          >

            <MoreHorizontal
              size={16}
            />

          </button>


          {menuChatId ===
            chat.id && (

            <div
              style={{
                position:
                  "absolute",
                right:
                  "5px",
                top:
                  "38px",
                zIndex:
                  20,
                padding:
                  "5px",
                borderRadius:
                  "8px",
                background:
                  "var(--card-bg, #1e1e1e)",
                border:
                  "1px solid #444",
                boxShadow:
                  "0 5px 20px rgba(0,0,0,0.3)"
              }}
            >

              <button
                onClick={() =>
                  deleteChat(
                    chat.id
                  )
                }
                style={{
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap:
                    "7px",
                  background:
                    "none",
                  border:
                    "none",
                  padding:
                    "8px 12px",
                  cursor:
                    "pointer",
                  color:
                    "#ff6b6b"
                }}
              >

                <Trash2
                  size={15}
                />

                Delete

              </button>

            </div>

          )}

        </div>

      )
    );

  };


  // =====================================================
  // UI
  // =====================================================

  return (

    <div
      className={`app theme-${theme}`}
    >

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            C
          </div>

          <span>
            CodeGuard
          </span>

        </div>


        <button
          className="new-chat"
          onClick={
            createNewChat
          }
        >

          <Plus size={18} />

          <span>
            New Chat
          </span>

        </button>


        <button
          className="search-button"
          onClick={() =>
            setSearchOpen(
              !searchOpen
            )
          }
        >

          <Search size={18} />

          <span>
            Search
          </span>

        </button>


        {searchOpen && (

          <div
            style={{
              padding:
                "8px 10px"
            }}
          >

            <input
              type="text"
              value={
                searchText
              }
              onChange={(e) =>
                setSearchText(
                  e.target.value
                )
              }
              placeholder="Search chats..."
              autoFocus
              style={{
                width:
                  "100%",
                boxSizing:
                  "border-box",
                padding:
                  "8px 10px",
                borderRadius:
                  "7px",
                border:
                  "1px solid #444",
                background:
                  "transparent",
                color:
                  "inherit",
                outline:
                  "none"
              }}
            />

          </div>

        )}


        <div className="history">

          {todayChats.length > 0 && (

            <>

              <div className="history-title">
                Today
              </div>

              {renderChatList(
                todayChats
              )}

            </>

          )}


          {yesterdayChats.length > 0 && (

            <>

              <div className="history-title">
                Yesterday
              </div>

              {renderChatList(
                yesterdayChats
              )}

            </>

          )}


          {previousChats.length > 0 && (

            <>

              <div className="history-title">
                Previous 7 Days
              </div>

              {renderChatList(
                previousChats
              )}

            </>

          )}


          {filteredChats.length === 0 && (

            <div
              style={{
                padding:
                  "15px",
                opacity:
                  0.6,
                fontSize:
                  "13px"
              }}
            >

              No conversations yet.

            </div>

          )}

        </div>


        <div className="sidebar-bottom">

          <button
            className="sidebar-button"
            onClick={() =>
              setSettingsOpen(
                true
              )
            }
          >

            <Settings size={18} />

            <span>
              Settings
            </span>

          </button>


          <button
            className="sidebar-button"
            onClick={() =>
              setProfileOpen(
                true
              )
            }
          >

            <User size={18} />

            <span>
              Profile
            </span>

          </button>

        </div>

      </aside>


      <main className="main">

        <header className="topbar">

          <div className="system-status">

            <span className="status-dot"></span>

            System Online

          </div>


          <button
            className="profile-button"
            onClick={() =>
              setProfileOpen(
                true
              )
            }
          >

            <User size={18} />

          </button>

        </header>


        <section className="chat-area">

          {messages.length === 0 && (

            <div className="welcome">

              <div className="welcome-icon">
                C
              </div>

              <h1>
                Analyze. Debug. Refactor.
              </h1>

              <p>
                Your AI-powered software engineering workspace.
              </p>

            </div>

          )}


          {messages.length > 0 && (

            <div className="messages">

              {messages.map(
                (msg, index) => (

                  <div
                    key={index}
                    className={`message ${msg.role}`}
                  >

                    <div className="message-avatar">

                      {msg.role ===
                      "user"
                        ? (
                          <User
                            size={16}
                          />
                        )
                        : "C"
                      }

                    </div>


                    <div className="message-content">

                      <div className="message-name">

                        {msg.role ===
                        "user"
                          ? "You"
                          : "CodeGuard"
                        }

                      </div>


                      <div
                        className="message-text"
                        style={{
                          whiteSpace:
                            "pre-line"
                        }}
                      >

                        {msg.text}

                      </div>


                      {msg.role ===
                        "assistant" &&
                        msg.aiReview && (

                        <div
                          style={{
                            marginTop:
                              "15px",
                            padding:
                              "10px 12px",
                            borderRadius:
                              "8px",
                            background:
                              "rgba(120, 90, 255, 0.08)",
                            border:
                              "1px solid rgba(120, 90, 255, 0.25)",
                            fontSize:
                              "12px",
                            opacity:
                              0.85
                          }}
                        >

                          <Sparkles
                            size={14}
                            style={{
                              verticalAlign:
                                "middle",
                              marginRight:
                                "6px"
                            }}
                          />

                          {isLeetCodeResponse(
                            msg.aiReview
                          )
                            ? "Gemini AI Solution"
                            : "Gemini AI Review"
                          }

                          {msg.aiReview.success
                            ? " completed"
                            : " unavailable"
                          }

                        </div>

                      )}


                      {msg.role ===
                        "assistant" &&
                        msg.improvedCode && (

                        <div
                          style={{
                            marginTop:
                              "16px",
                            border:
                              "1px solid rgba(120, 90, 255, 0.25)",
                            borderRadius:
                              "10px",
                            overflow:
                              "hidden",
                            background:
                              "rgba(0,0,0,0.15)"
                          }}
                        >

                          <div
                            style={{
                              display:
                                "flex",
                              justifyContent:
                                "space-between",
                              alignItems:
                                "center",
                              padding:
                                "10px 12px",
                              borderBottom:
                                "1px solid rgba(120, 90, 255, 0.15)"
                            }}
                          >

                            <div
                              style={{
                                display:
                                  "flex",
                                alignItems:
                                  "center",
                                gap:
                                  "7px",
                                fontWeight:
                                  "600"
                              }}
                            >

                              <Sparkles
                                size={16}
                              />

                              {isLeetCodeResponse(
                                msg.aiReview
                              )
                                ? "AI Solution Code"
                                : "AI Fixed Code"
                              }

                            </div>


                            <button
                              className="icon-button"
                              onClick={() =>
                                copyCode(
                                  msg.improvedCode
                                )
                              }
                              title="Copy code"
                            >

                              {copied
                                ? (
                                  <Check
                                    size={17}
                                  />
                                )
                                : (
                                  <Copy
                                    size={17}
                                  />
                                )
                              }

                              <span
                                style={{
                                  marginLeft:
                                    "5px"
                                }}
                              >

                                {copied
                                  ? "Copied"
                                  : "Copy"
                                }

                              </span>

                            </button>

                          </div>


                          <pre
                            style={{
                              margin:
                                0,
                              padding:
                                "16px",
                              overflowX:
                                "auto",
                              fontSize:
                                "13px",
                              lineHeight:
                                "1.6",
                              whiteSpace:
                                "pre-wrap"
                            }}
                          >

                            <code>
                              {msg.improvedCode}
                            </code>

                          </pre>

                        </div>

                      )}


                      {msg.role ===
                        "assistant" &&
                        msg.refactoredCode && (

                        <button
                          className="icon-button"
                          onClick={() =>
                            copyCode(
                              msg.refactoredCode
                            )
                          }
                          style={{
                            marginTop:
                              "8px"
                          }}
                        >

                          {copied
                            ? (
                              <Check
                                size={18}
                              />
                            )
                            : (
                              <Copy
                                size={18}
                              />
                            )
                          }

                          <span
                            style={{
                              marginLeft:
                                "6px"
                            }}
                          >

                            {copied
                              ? "Copied"
                              : "Copy Code"
                            }

                          </span>

                        </button>

                      )}

                    </div>

                  </div>

                )
              )}


              {loading && (

                <div className="message assistant">

                  <div className="message-avatar">
                    C
                  </div>

                  <div className="message-content">

                    <div className="message-name">
                      CodeGuard
                    </div>

                    <div className="message-text">

                      CodeGuard AI is analyzing / solving...

                    </div>

                  </div>

                </div>

              )}

            </div>

          )}


          {messages.length === 0 && (

            <div className="quick-actions">

              <button
                className="quick-card"
                onClick={() =>
                  handleQuickAction(
                    "bugs"
                  )
                }
                disabled={loading}
              >

                <Bug size={20} />

                <div>

                  <strong>
                    Find Bugs
                  </strong>

                  <span>
                    Detect potential problems
                  </span>

                </div>

              </button>


              <button
                className="quick-card"
                onClick={() =>
                  handleQuickAction(
                    "complexity"
                  )
                }
                disabled={loading}
              >

                <Zap size={20} />

                <div>

                  <strong>
                    Analyze Complexity
                  </strong>

                  <span>
                    Check time and space
                  </span>

                </div>

              </button>


              <button
                className="quick-card"
                onClick={() =>
                  handleQuickAction(
                    "refactor"
                  )
                }
                disabled={loading}
              >

                <RefreshCw size={20} />

                <div>

                  <strong>
                    Refactor Code
                  </strong>

                  <span>
                    Improve code quality
                  </span>

                </div>

              </button>


              <button
                className="quick-card"
                onClick={() =>
                  handleQuickAction(
                    "tests"
                  )
                }
                disabled={loading}
              >

                <FlaskConical size={20} />

                <div>

                  <strong>
                    Generate Tests
                  </strong>

                  <span>
                    Create test cases
                  </span>

                </div>

              </button>

            </div>

          )}


          <div className="input-container">

            {attachedFile && (

              <div
                style={{
                  display:
                    "flex",
                  alignItems:
                    "center",
                  justifyContent:
                    "space-between",
                  gap:
                    "10px",
                  padding:
                    "8px 12px",
                  marginBottom:
                    "8px",
                  borderRadius:
                    "8px",
                  background:
                    "rgba(120, 90, 255, 0.08)",
                  border:
                    "1px solid rgba(120, 90, 255, 0.25)",
                  fontSize:
                    "13px"
                }}
              >

                <div
                  style={{
                    display:
                      "flex",
                    alignItems:
                      "center",
                    gap:
                      "8px",
                    minWidth:
                      0
                  }}
                >

                  <Paperclip
                    size={15}
                  />

                  <span
                    style={{
                      overflow:
                        "hidden",
                      textOverflow:
                        "ellipsis",
                      whiteSpace:
                        "nowrap"
                    }}
                  >

                    {attachedFile.name}

                  </span>

                </div>


                <button
                  onClick={
                    removeAttachedFile
                  }
                  title="Remove file"
                  style={{
                    display:
                      "flex",
                    alignItems:
                      "center",
                    justifyContent:
                      "center",
                    border:
                      "none",
                    background:
                      "transparent",
                    color:
                      "inherit",
                    cursor:
                      "pointer",
                    padding:
                      "3px"
                  }}
                >

                  <X
                    size={16}
                  />

                </button>

              </div>

            )}


            <textarea
              value={
                message
              }
              onChange={(e) =>
                setMessage(
                  e.target.value
                )
              }
              onKeyDown={(e) => {

                if (
                  e.key === "Enter" &&
                  !e.shiftKey
                ) {

                  e.preventDefault();

                  handleSend();

                }

              }}
              placeholder="Paste your code or LeetCode question + code..."
            />


            <div className="input-footer">

              <button
                className="icon-button"
                title="Attach code file"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={loading}
              >

                <Paperclip
                  size={19}
                />

              </button>


              <input
                ref={fileInputRef}
                type="file"
                accept=".py,.java,.cpp,.cc,.cxx,.c,.js,.jsx,.ts,.tsx,.cs,.txt"
                onChange={
                  handleFileUpload
                }
                style={{
                  display:
                    "none"
                }}
              />


              <select
                className="language-select"
                value={
                  language
                }
                onChange={(e) =>
                  setLanguage(
                    e.target.value
                  )
                }
                disabled={loading}
              >

                {supportedLanguages.map(
                  (lang) => (

                    <option
                      key={lang}
                      value={lang}
                    >

                      {lang}

                    </option>

                  )
                )}

              </select>


              <button
                className="send-button"
                onClick={
                  handleSend
                }
                disabled={
                  loading ||
                  !message.trim()
                }
              >

                <Send size={18} />

              </button>

            </div>

          </div>


          <div className="disclaimer">

            CodeGuard can make mistakes. Always review generated code.

          </div>

        </section>

      </main>


      {/* =====================================================
          PROFILE MODAL
      ===================================================== */}

      {profileOpen && (

        <div
          style={{
            position:
              "fixed",
            inset:
              0,
            background:
              "rgba(0,0,0,0.55)",
            display:
              "flex",
            alignItems:
              "center",
            justifyContent:
              "center",
            zIndex:
              100
          }}
          onClick={() =>
            setProfileOpen(false)
          }
        >

          <div
            style={{
              width:
                "360px",
              padding:
                "25px",
              borderRadius:
                "14px",
              background:
                "#1a1a1a",
              border:
                "1px solid #333",
              boxShadow:
                "0 20px 60px rgba(0,0,0,0.5)"
            }}
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div
              style={{
                display:
                  "flex",
                justifyContent:
                  "space-between",
                alignItems:
                  "center",
                marginBottom:
                  "25px"
              }}
            >

              <h2>
                Profile
              </h2>

              <button
                onClick={() =>
                  setProfileOpen(
                    false
                  )
                }
                style={{
                  background:
                    "none",
                  border:
                    "none",
                  color:
                    "inherit",
                  cursor:
                    "pointer"
                }}
              >

                <X size={20} />

              </button>

            </div>


            <div
              style={{
                textAlign:
                  "center"
              }}
            >

              <div
                style={{
                  width:
                    "70px",
                  height:
                    "70px",
                  borderRadius:
                    "50%",
                  margin:
                    "0 auto 15px",
                  display:
                    "flex",
                  alignItems:
                    "center",
                  justifyContent:
                    "center",
                  background:
                    "#333",
                  fontSize:
                    "25px"
                }}
              >

                {user?.name
                  ? user.name
                      .charAt(0)
                      .toUpperCase()
                  : "A"}

              </div>


              <h3>
                {user?.name ||
                  "CodeGuard User"}
              </h3>


              <p
                style={{
                  opacity:
                    0.7
                }}
              >

                {user?.email ||
                  "CodeGuard User"}

              </p>


              <p
                style={{
                  opacity:
                    0.6,
                  fontSize:
                    "13px"
                }}
              >

                Frontend Developer & ML Engineer

              </p>


              <button
                onClick={() => {

                  setProfileOpen(false);

                  onLogout();

                }}
                style={{
                  width:
                    "100%",
                  marginTop:
                    "20px",
                  padding:
                    "11px",
                  borderRadius:
                    "8px",
                  border:
                    "1px solid #555",
                  background:
                    "transparent",
                  color:
                    "#ff6b6b",
                  cursor:
                    "pointer",
                  fontSize:
                    "14px"
                }}
              >

                <LogOut
                  size={16}
                  style={{
                    marginRight:
                      "7px",
                    verticalAlign:
                      "middle"
                  }}
                />

                Logout

              </button>

            </div>

          </div>

        </div>

      )}


      {/* =====================================================
          SETTINGS MODAL
      ===================================================== */}

      {settingsOpen && (

        <div
          style={{
            position:
              "fixed",
            inset:
              0,
            background:
              "rgba(0,0,0,0.55)",
            display:
              "flex",
            alignItems:
              "center",
            justifyContent:
              "center",
            zIndex:
              100
          }}
          onClick={() =>
            setSettingsOpen(false)
          }
        >

          <div
            style={{
              width:
                "380px",
              padding:
                "25px",
              borderRadius:
                "14px",
              background:
                "#1a1a1a",
              border:
                "1px solid #333",
              boxShadow:
                "0 20px 60px rgba(0,0,0,0.5)"
            }}
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div
              style={{
                display:
                  "flex",
                justifyContent:
                  "space-between",
                alignItems:
                  "center",
                marginBottom:
                  "25px"
              }}
            >

              <h2>
                Settings
              </h2>


              <button
                onClick={() =>
                  setSettingsOpen(
                    false
                  )
                }
                style={{
                  background:
                    "none",
                  border:
                    "none",
                  color:
                    "inherit",
                  cursor:
                    "pointer"
                }}
              >

                <X size={20} />

              </button>

            </div>


            <div
              style={{
                display:
                  "flex",
                justifyContent:
                  "space-between",
                alignItems:
                  "center",
                padding:
                  "15px 0",
                borderBottom:
                  "1px solid #333"
              }}
            >

              <div>

                <strong>
                  Dark Mode
                </strong>

                <div
                  style={{
                    fontSize:
                      "12px",
                    opacity:
                      0.6,
                    marginTop:
                      "4px"
                  }}
                >

                  Use dark interface

                </div>

              </div>


              <input
                type="checkbox"
                checked={
                  darkMode
                }
                onChange={(e) =>
                  handleDarkModeChange(
                    e.target.checked
                  )
                }
              />

            </div>


            <div
              style={{
                padding:
                  "18px 0",
                borderBottom:
                  "1px solid #333"
              }}
            >

              <strong>
                Theme
              </strong>


              <div
                style={{
                  fontSize:
                    "12px",
                  opacity:
                    0.6,
                  marginTop:
                    "4px"
                }}
              >

                Choose your preferred interface theme

              </div>


              <select
                value={
                  theme
                }
                onChange={(e) =>
                  setTheme(
                    e.target.value
                  )
                }
                style={{
                  display:
                    "block",
                  width:
                    "100%",
                  marginTop:
                    "10px",
                  padding:
                    "9px",
                  borderRadius:
                    "7px",
                  background:
                    "#222",
                  color:
                    "white",
                  border:
                    "1px solid #444",
                  outline:
                    "none"
                }}
              >

                <option value="dark">
                  🌑 Dark
                </option>

                <option value="light">
                  ☀️ Light
                </option>

                <option value="midnight">
                  💙 Midnight Blue
                </option>

                <option value="purple">
                  🟣 Purple
                </option>

              </select>

            </div>


            <div
              style={{
                padding:
                  "18px 0"
              }}
            >

              <strong>
                Default Language
              </strong>


              <select
                value={
                  language
                }
                onChange={(e) =>
                  setLanguage(
                    e.target.value
                  )
                }
                style={{
                  display:
                    "block",
                  width:
                    "100%",
                  marginTop:
                    "10px",
                  padding:
                    "9px",
                  borderRadius:
                    "7px",
                  background:
                    "#222",
                  color:
                    "white",
                  border:
                    "1px solid #444",
                  outline:
                    "none"
                }}
              >

                {supportedLanguages.map(
                  (lang) => (

                    <option
                      key={lang}
                      value={lang}
                    >

                      {lang}

                    </option>

                  )
                )}

              </select>

            </div>


            <button
              onClick={() => {

                if (
                  window.confirm(
                    "Delete all chat history?"
                  )
                ) {

                  setChats([]);

                  setMessages([]);

                  setCurrentChatId(
                    null
                  );

                  localStorage.removeItem(
                    "codeguard_chats"
                  );

                }

              }}
              style={{
                width:
                  "100%",
                padding:
                  "10px",
                borderRadius:
                  "8px",
                border:
                  "1px solid #555",
                background:
                  "transparent",
                color:
                  "#ff6b6b",
                cursor:
                  "pointer"
              }}
            >

              <Trash2
                size={15}
                style={{
                  marginRight:
                    "7px",
                  verticalAlign:
                    "middle"
                }}
              />

              Clear All History

            </button>

          </div>

        </div>

      )}

    </div>

  );

}


export default App;