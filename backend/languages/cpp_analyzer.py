import re


def analyze_cpp_code(code):

    bugs = []
    security = []
    suggestions = []

    lines = code.splitlines()

    # ==========================================
    # SYNTAX CHECK
    # ==========================================

    syntax_valid = True
    syntax_error = None

    # Curly braces
    if code.count("{") != code.count("}"):

        syntax_valid = False

        syntax_error = "Mismatched curly braces {}"

    # Parentheses
    elif code.count("(") != code.count(")"):

        syntax_valid = False

        syntax_error = "Mismatched parentheses ()"

    # ==========================================
    # BUG DETECTION
    # ==========================================

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

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
        # Array index
        # --------------------------------------

        if re.search(r"\w+\s*\[.*\]", stripped):

            bugs.append({
                "type": "Array Access",
                "line": line_number,
                "message": "Array indexing detected. Invalid indexes may cause undefined behavior.",
                "suggestion": "Validate the array index before accessing the element."
            })

        # --------------------------------------
        # Pointer dereference
        # --------------------------------------

        if re.search(r"\*\s*[a-zA-Z_]\w*", stripped):

            suggestions.append({
                "type": "Pointer Usage",
                "line": line_number,
                "message": "Pointer usage detected.",
                "suggestion": "Make sure the pointer is initialized and not null before dereferencing."
            })

        # --------------------------------------
        # Debug output
        # --------------------------------------

        if "cout" in stripped:

            suggestions.append({
                "type": "Console Output",
                "line": line_number,
                "message": "Console output detected.",
                "suggestion": "Remove unnecessary debug output in production."
            })

        # --------------------------------------
        # gets()
        # --------------------------------------

        if re.search(r"\bgets\s*\(", stripped):

            security.append({
                "type": "Unsafe Input",
                "line": line_number,
                "message": "gets() is unsafe and can cause buffer overflow.",
                "suggestion": "Use std::getline() or another bounds-safe input method."
            })

        # --------------------------------------
        # strcpy()
        # --------------------------------------

        if "strcpy(" in stripped:

            security.append({
                "type": "Buffer Overflow Risk",
                "line": line_number,
                "message": "strcpy() does not check destination buffer size.",
                "suggestion": "Use a safer alternative such as std::string or carefully bounded copying."
            })

        # --------------------------------------
        # system()
        # --------------------------------------

        if re.search(r"\bsystem\s*\(", stripped):

            security.append({
                "type": "Command Execution",
                "line": line_number,
                "message": "system() can execute operating-system commands.",
                "suggestion": "Avoid system() with untrusted input and validate all external data."
            })

        # --------------------------------------
        # malloc()
        # --------------------------------------

        if "malloc(" in stripped:

            suggestions.append({
                "type": "Manual Memory Management",
                "line": line_number,
                "message": "malloc() detected.",
                "suggestion": "Prefer RAII and standard containers such as vector or string where possible."
            })

        # --------------------------------------
        # delete
        # --------------------------------------

        if re.search(r"\bdelete\b", stripped):

            suggestions.append({
                "type": "Manual Memory Management",
                "line": line_number,
                "message": "Manual memory deallocation detected.",
                "suggestion": "Prefer smart pointers such as std::unique_ptr or std::shared_ptr."
            })

        # --------------------------------------
        # Empty catch
        # --------------------------------------

        if stripped == "catch":

            bugs.append({
                "type": "Exception Handling",
                "line": line_number,
                "message": "Exception handling may not contain meaningful recovery logic.",
                "suggestion": "Handle the exception or log the error appropriately."
            })

    # ==========================================
    # SECURITY PATTERNS
    # ==========================================

    dangerous_patterns = [
        "exec(",
        "popen(",
        "system(",
        "strcpy(",
        "gets("
    ]

    for line_number, line in enumerate(lines, start=1):

        for pattern in dangerous_patterns:

            if pattern in line:

                already_added = any(
                    item["line"] == line_number
                    and pattern.replace("(", "") in item["message"]
                    for item in security
                )

                if not already_added:
                    security.append({
                        "type": "Potential Security Risk",
                        "line": line_number,
                        "message": f"Potentially dangerous function detected: {pattern}",
                        "suggestion": "Validate input and use safer alternatives where possible."
                    })

    # ==========================================
    # COMPLEXITY
    # ==========================================

    loop_count = 0

    for line in lines:

        if re.search(r"\b(for|while)\b", line):

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

    if "vector" in code or "array" in code:

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
            "suggestion": "Consider splitting the code into smaller functions or classes."
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