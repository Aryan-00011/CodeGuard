import re


def analyze_java_code(code):

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

    # ==========================================
    # BUG DETECTION
    # ==========================================

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # String comparison using ==
        if "String" in stripped and "==" in stripped:

            bugs.append({
                "type": "String Comparison",
                "line": line_number,
                "message": "String comparison using == may compare references.",
                "suggestion": "Use .equals() for String value comparison."
            })

        # Possible division by zero
        if "/" in stripped:

            bugs.append({
                "type": "Division Operation",
                "line": line_number,
                "message": "Division operation detected.",
                "suggestion": "Make sure the denominator cannot be zero."
            })

        # Debug statements
        if "System.out.println" in stripped:

            suggestions.append({
                "type": "Debug Statement",
                "line": line_number,
                "message": "Console output detected.",
                "suggestion": "Remove unnecessary debug statements in production."
            })

    # ==========================================
    # SECURITY CHECK
    # ==========================================

    dangerous_patterns = [
        "Runtime.getRuntime().exec",
        "ProcessBuilder",
        "ObjectInputStream",
        "ScriptEngine"
    ]

    for line_number, line in enumerate(lines, start=1):

        for pattern in dangerous_patterns:

            if pattern in line:

                security.append({
                    "type": "Potential Security Risk",
                    "line": line_number,
                    "message": f"Dangerous API detected: {pattern}",
                    "suggestion": "Validate input and avoid executing untrusted data."
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

    space_complexity = "O(1) auxiliary space"

    # ==========================================
    # GENERAL SUGGESTIONS
    # ==========================================

    if len(code) > 300:

        suggestions.append({
            "type": "Maintainability",
            "line": None,
            "message": "Large source code detected.",
            "suggestion": "Consider splitting the code into smaller methods or classes."
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