import re


def analyze_c_code(code):

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
        # Division operation
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
                "message": "Array indexing detected. Invalid indexes may cause undefined behavior.",
                "suggestion": "Make sure the array index is within valid bounds."
            })

        # --------------------------------------
        # Pointer usage
        # --------------------------------------

        if re.search(r"\*\s*[a-zA-Z_]\w*", stripped):

            suggestions.append({
                "type": "Pointer Usage",
                "line": line_number,
                "message": "Pointer usage detected.",
                "suggestion": "Make sure the pointer is initialized before dereferencing."
            })

        # --------------------------------------
        # printf debug/output
        # --------------------------------------

        if "printf(" in stripped:

            suggestions.append({
                "type": "Console Output",
                "line": line_number,
                "message": "printf() detected.",
                "suggestion": "Remove unnecessary console output in production."
            })

        # --------------------------------------
        # scanf input
        # --------------------------------------

        if "scanf(" in stripped:

            suggestions.append({
                "type": "User Input",
                "line": line_number,
                "message": "scanf() detected.",
                "suggestion": "Validate user input carefully before using it."
            })

        # --------------------------------------
        # malloc
        # --------------------------------------

        if "malloc(" in stripped:

            suggestions.append({
                "type": "Manual Memory Management",
                "line": line_number,
                "message": "malloc() detected.",
                "suggestion": "Make sure allocated memory is properly released using free()."
            })

        # --------------------------------------
        # free
        # --------------------------------------

        if re.search(r"\bfree\s*\(", stripped):

            suggestions.append({
                "type": "Memory Deallocation",
                "line": line_number,
                "message": "free() detected.",
                "suggestion": "Ensure the pointer is valid and is not used after free()."
            })

    # ==========================================
    # SECURITY CHECKS
    # ==========================================

    # gets()
    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        if re.search(r"\bgets\s*\(", stripped):

            security.append({
                "type": "Unsafe Input",
                "line": line_number,
                "message": "gets() is unsafe and may cause buffer overflow.",
                "suggestion": "Use fgets() with a proper buffer size."
            })

        # strcpy()
        if re.search(r"\bstrcpy\s*\(", stripped):

            security.append({
                "type": "Buffer Overflow Risk",
                "line": line_number,
                "message": "strcpy() does not check destination buffer size.",
                "suggestion": "Use bounded copying or safer string handling."
            })

        # strcat()
        if re.search(r"\bstrcat\s*\(", stripped):

            security.append({
                "type": "Buffer Overflow Risk",
                "line": line_number,
                "message": "strcat() may overflow the destination buffer.",
                "suggestion": "Use bounded string operations and validate buffer size."
            })

        # sprintf()
        if re.search(r"\bsprintf\s*\(", stripped):

            security.append({
                "type": "Format String Risk",
                "line": line_number,
                "message": "sprintf() can cause buffer overflow.",
                "suggestion": "Use snprintf() with an explicit buffer size."
            })

        # system()
        if re.search(r"\bsystem\s*\(", stripped):

            security.append({
                "type": "Command Execution",
                "line": line_number,
                "message": "system() can execute operating-system commands.",
                "suggestion": "Avoid system() with untrusted input."
            })

    # ==========================================
    # HARD-CODED SECRET DETECTION
    # ==========================================

    secret_patterns = [
        r'password\s*=\s*["\']',
        r'api_key\s*=\s*["\']',
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
                    "suggestion": "Store sensitive values securely instead of hardcoding them."
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

    if "malloc(" in code:

        space_complexity = "O(n) depending on allocated memory"

    elif re.search(r"\w+\s+\w+\s*\[\s*\d+\s*\]", code):

        space_complexity = "O(n) depending on arrays"

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
            "suggestion": "Consider splitting the program into smaller functions."
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