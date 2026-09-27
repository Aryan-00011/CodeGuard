from analyzer.python_analyzer import analyze_python_code

from languages.java_analyzer import analyze_java_code
from languages.cpp_analyzer import analyze_cpp_code
from languages.c_analyzer import analyze_c_code
from languages.javascript_analyzer import analyze_javascript_code
from languages.typescript_analyzer import analyze_typescript_code
from languages.csharp_analyzer import analyze_csharp_code


def analyze_by_language(code, language):

    # ==========================================
    # PYTHON
    # ==========================================

    if language == "Python":

        return analyze_python_code(code)

    # ==========================================
    # JAVA
    # ==========================================

    elif language == "Java":

        return analyze_java_code(code)

    # ==========================================
    # C++
    # ==========================================

    elif language == "C++":

        return analyze_cpp_code(code)

    # ==========================================
    # C
    # ==========================================

    elif language == "C":

        return analyze_c_code(code)

    # ==========================================
    # JAVASCRIPT
    # ==========================================

    elif language == "JavaScript":

        return analyze_javascript_code(code)

    # ==========================================
    # TYPESCRIPT
    # ==========================================

    elif language == "TypeScript":

        return analyze_typescript_code(code)

    # ==========================================
    # C#
    # ==========================================

    elif language == "C#":

        return analyze_csharp_code(code)

    # ==========================================
    # UNSUPPORTED
    # ==========================================

    else:

        return {
            "syntax": {
                "valid": False,
                "error": "Unsupported programming language."
            },

            "bugs": [],

            "complexity": {
                "time": "Not available",
                "space": "Not available"
            },

            "security": [],

            "suggestions": [
                f"{language} is not supported by CodeGuard."
            ]
        }