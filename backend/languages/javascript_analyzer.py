import re


def analyze_javascript_code(code):

    bugs = []
    security = []
    suggestions = []

    lines = code.splitlines()

    # ==========================================
    # SYNTAX CHECK
    # ==========================================

    syntax_valid = True
    syntax_error = None

    if code.count("{") != code.count("}"):

        syntax_valid = False
        syntax_error = "Mismatched curly braces {}"

    elif code.count("(") != code.count(")"):

        syntax_valid = False
        syntax_error = "Mismatched parentheses ()"

    elif code.count("[") != code.count("]"):

        syntax_valid = False
        syntax_error = "Mismatched square brackets []"

    # ==========================================
    # BUG DETECTION
    # ==========================================

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # --------------------------------------
        # == instead of ===
        # --------------------------------------

        if "==" in stripped and "===" not in stripped:

            bugs.append({
                "type": "Loose Equality",
                "line": line_number,
                "message": "Loose equality operator == detected.",
                "suggestion": "Prefer === for strict equality comparison."
            })

        # --------------------------------------
        # != instead of !==
        # --------------------------------------

        if "!=" in stripped and "!==" not in stripped:

            bugs.append({
                "type": "Loose Inequality",
                "line": line_number,
                "message": "Loose inequality operator != detected.",
                "suggestion": "Prefer !== for strict inequality comparison."
            })

        # --------------------------------------
        # Array access
        # --------------------------------------

        if re.search(r"\w+\s*\[.*\]", stripped):

            bugs.append({
                "type": "Array Access",
                "line": line_number,
                "message": "Array indexing detected.",
                "suggestion": "Make sure the index exists before accessing the array."
            })

        # --------------------------------------
        # Division
        # --------------------------------------

        if "/" in stripped and not stripped.startswith("//"):

            bugs.append({
                "type": "Division Operation",
                "line": line_number,
                "message": "Division operation detected.",
                "suggestion": "Make sure the denominator is not zero."
            })

        # --------------------------------------
        # var usage
        # --------------------------------------

        if re.search(r"\bvar\b", stripped):

            suggestions.append({
                "type": "Variable Declaration",
                "line": line_number,
                "message": "var keyword detected.",
                "suggestion": "Prefer let or const for modern JavaScript."
            })

        # --------------------------------------
        # console.log
        # --------------------------------------

        if "console.log(" in stripped:

            suggestions.append({
                "type": "Debug Statement",
                "line": line_number,
                "message": "console.log() detected.",
                "suggestion": "Remove unnecessary console logs from production code."
            })

        # --------------------------------------
        # document.write
        # --------------------------------------

        if "document.write(" in stripped:

            security.append({
                "type": "Unsafe DOM Operation",
                "line": line_number,
                "message": "document.write() can create security and maintainability issues.",
                "suggestion": "Prefer safe DOM manipulation methods."
            })

    # ==========================================
    # SECURITY CHECKS
    # ==========================================

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # eval
        if re.search(r"\beval\s*\(", stripped):

            security.append({
                "type": "Code Injection",
                "line": line_number,
                "message": "eval() executes dynamically generated JavaScript.",
                "suggestion": "Avoid eval() and use safer alternatives."
            })

        # Function constructor
        if "new Function(" in stripped:

            security.append({
                "type": "Dynamic Code Execution",
                "line": line_number,
                "message": "Function constructor can execute dynamic code.",
                "suggestion": "Avoid dynamically constructing executable code."
            })

        # innerHTML
        if "innerHTML" in stripped:

            security.append({
                "type": "Potential XSS",
                "line": line_number,
                "message": "innerHTML may introduce Cross-Site Scripting risks with untrusted input.",
                "suggestion": "Validate input or use textContent when HTML is not required."
            })

        # localStorage secrets
        if "localStorage.setItem" in stripped:

            security.append({
                "type": "Client-Side Storage",
                "line": line_number,
                "message": "Sensitive data may be stored in localStorage.",
                "suggestion": "Avoid storing passwords, tokens, or sensitive secrets in localStorage."
            })

    # ==========================================
    # HARD-CODED SECRETS
    # ==========================================

    secret_patterns = [
        r'password\s*=\s*["\']',
        r'api[_-]?key\s*=\s*["\']',
        r'secret\s*=\s*["\']',
        r'token\s*=\s*["\']'
    ]

    for line_number, line in enumerate(lines, start=1):

        for pattern in secret_patterns:

            if re.search(pattern, line, re.IGNORECASE):

                security.append({
                    "type": "Hardcoded Secret",
                    "line": line_number,
                    "message": "Possible hardcoded secret detected.",
                    "suggestion": "Store secrets securely using environment variables or a secret manager."
                })

                break

    # ==========================================
    # COMPLEXITY
    # ==========================================

    loop_count = 0

    for line in lines:

        if re.search(r"\b(for|while|do)\b", line):

            loop_count += 1

    if loop_count == 0:

        time_complexity = "O(1) or depends on called functions"

    elif loop_count == 1:

        time_complexity = "Approximately O(n)"

    else:

        time_complexity = "Potentially O(n²) or higher"

    # ==========================================
    # SPACE COMPLEXITY
    # ==========================================

    if "new Array" in code or "[" in code:

        space_complexity = "O(n) depending on data structures"

    else:

        space_complexity = "O(1) auxiliary space"

    # ==========================================
    # GENERAL SUGGESTIONS
    # ==========================================

    if len(code) > 300:

        suggestions.append({
            "type": "Maintainability",
            "line": None,
            "message": "Large source code detected.",
            "suggestion": "Consider splitting the code into smaller functions or modules."
        })

    # ==========================================
    # FINAL RESULT
    # ==========================================

    return {

        "syntax": {
            "valid": syntax_valid,
            "error": syntax_error
        },

        "bugs": bugs,

        "complexity": {
            "time": time_complexity,
            "space": space_complexity
        },

        "security": security,

        "suggestions": suggestions
    }