import re


def analyze_csharp_code(code):

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
        # String == comparison
        # --------------------------------------

        if "string" in stripped.lower() and "==" in stripped:

            bugs.append({
                "type": "String Comparison",
                "line": line_number,
                "message": "String comparison using == detected.",
                "suggestion": "Use appropriate string comparison methods when exact comparison semantics are required."
            })

        # --------------------------------------
        # Possible division by zero
        # --------------------------------------

        if "/" in stripped and not stripped.startswith("//"):

            bugs.append({
                "type": "Division Operation",
                "line": line_number,
                "message": "Division operation detected.",
                "suggestion": "Make sure the denominator cannot be zero."
            })

        # --------------------------------------
        # Array access
        # --------------------------------------

        if re.search(r"\w+\s*\[.*\]", stripped):

            bugs.append({
                "type": "Array Access",
                "line": line_number,
                "message": "Array indexing detected.",
                "suggestion": "Make sure the index is within valid bounds."
            })

        # --------------------------------------
        # Null usage
        # --------------------------------------

        if "= null" in stripped:

            suggestions.append({
                "type": "Null Handling",
                "line": line_number,
                "message": "Variable is assigned null.",
                "suggestion": "Make sure null values are handled before accessing the object."
            })

        # --------------------------------------
        # Console output
        # --------------------------------------

        if "Console.WriteLine" in stripped:

            suggestions.append({
                "type": "Debug Statement",
                "line": line_number,
                "message": "Console output detected.",
                "suggestion": "Remove unnecessary console output from production code."
            })

        # --------------------------------------
        # Empty catch
        # --------------------------------------

        if re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", stripped):

            bugs.append({
                "type": "Empty Exception Handler",
                "line": line_number,
                "message": "Empty catch block detected.",
                "suggestion": "Handle or log the exception instead of silently ignoring it."
            })

    # ==========================================
    # SECURITY
    # ==========================================

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # Process.Start
        if "Process.Start(" in stripped:

            security.append({
                "type": "Command Execution",
                "line": line_number,
                "message": "Process.Start() can launch external processes.",
                "suggestion": "Validate all external input before launching processes."
            })

        # SQL concatenation
        if "SqlCommand" in stripped and "+" in stripped:

            security.append({
                "type": "SQL Injection Risk",
                "line": line_number,
                "message": "SQL command appears to use string concatenation.",
                "suggestion": "Use parameterized SQL queries."
            })

        # BinaryFormatter
        if "BinaryFormatter" in stripped:

            security.append({
                "type": "Unsafe Deserialization",
                "line": line_number,
                "message": "BinaryFormatter can be dangerous with untrusted data.",
                "suggestion": "Use a safer serialization format."
            })

        # HTML injection
        if "Html.Raw(" in stripped:

            security.append({
                "type": "Potential XSS",
                "line": line_number,
                "message": "Raw HTML rendering may introduce XSS risks.",
                "suggestion": "Sanitize untrusted HTML before rendering it."
            })

    # ==========================================
    # HARD-CODED SECRETS
    # ==========================================

    secret_patterns = [
        r'password\s*=\s*"',
        r'api[_-]?key\s*=\s*"',
        r'secret\s*=\s*"',
        r'token\s*=\s*"'
    ]

    for line_number, line in enumerate(lines, start=1):

        for pattern in secret_patterns:

            if re.search(pattern, line, re.IGNORECASE):

                security.append({
                    "type": "Hardcoded Secret",
                    "line": line_number,
                    "message": "Possible hardcoded secret detected.",
                    "suggestion": "Use secure configuration or environment variables."
                })

                break

    # ==========================================
    # COMPLEXITY
    # ==========================================

    loop_count = 0

    for line in lines:

        if re.search(r"\b(for|foreach|while|do)\b", line):

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

    if "List<" in code or "[]" in code or "new List" in code:

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
            "suggestion": "Consider splitting the code into smaller classes or methods."
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