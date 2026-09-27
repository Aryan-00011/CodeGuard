import re


def analyze_typescript_code(code):

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
        # Loose equality
        # --------------------------------------

        if "==" in stripped and "===" not in stripped:

            bugs.append({
                "type": "Loose Equality",
                "line": line_number,
                "message": "Loose equality operator == detected.",
                "suggestion": "Prefer === for strict equality comparison."
            })

        # --------------------------------------
        # Loose inequality
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
                "suggestion": "Validate indexes before accessing array elements."
            })

        # --------------------------------------
        # Division
        # --------------------------------------

        if "/" in stripped and not stripped.startswith("//"):

            bugs.append({
                "type": "Division Operation",
                "line": line_number,
                "message": "Division operation detected.",
                "suggestion": "Make sure the denominator cannot be zero."
            })

        # --------------------------------------
        # any type
        # --------------------------------------

        if re.search(r":\s*any\b", stripped):

            suggestions.append({
                "type": "Type Safety",
                "line": line_number,
                "message": "The any type disables TypeScript type checking.",
                "suggestion": "Use a specific type whenever possible."
            })

        # --------------------------------------
        # console.log
        # --------------------------------------

        if "console.log(" in stripped:

            suggestions.append({
                "type": "Debug Statement",
                "line": line_number,
                "message": "console.log() detected.",
                "suggestion": "Remove unnecessary console output from production code."
            })

        # --------------------------------------
        # @ts-ignore
        # --------------------------------------

        if "@ts-ignore" in stripped:

            suggestions.append({
                "type": "Type Checking Suppression",
                "line": line_number,
                "message": "@ts-ignore disables TypeScript checking for the following line.",
                "suggestion": "Fix the underlying type issue instead of suppressing it."
            })

    # ==========================================
    # SECURITY
    # ==========================================

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # eval
        if re.search(r"\beval\s*\(", stripped):

            security.append({
                "type": "Code Injection",
                "line": line_number,
                "message": "eval() executes dynamically generated code.",
                "suggestion": "Avoid eval() and use safer alternatives."
            })

        # innerHTML
        if "innerHTML" in stripped:

            security.append({
                "type": "Potential XSS",
                "line": line_number,
                "message": "innerHTML can create XSS risks when handling untrusted content.",
                "suggestion": "Validate input or use textContent where appropriate."
            })

        # dangerouslySetInnerHTML
        if "dangerouslySetInnerHTML" in stripped:

            security.append({
                "type": "Potential XSS",
                "line": line_number,
                "message": "dangerouslySetInnerHTML can introduce XSS if content is not sanitized.",
                "suggestion": "Sanitize untrusted HTML before rendering it."
            })

        # localStorage
        if "localStorage.setItem" in stripped:

            security.append({
                "type": "Client-Side Storage",
                "line": line_number,
                "message": "Sensitive information may be stored in localStorage.",
                "suggestion": "Avoid storing sensitive tokens or passwords in localStorage."
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
                    "suggestion": "Use environment variables or secure secret management."
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
    # SPACE
    # ==========================================

    if "[]" in code or "Array<" in code:

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
            "suggestion": "Split the code into smaller functions or modules."
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