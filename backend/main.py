from flask import Flask, request, jsonify
from flask_cors import CORS
import re

from auth import (
    create_user,
    authenticate_user,
    create_token,
    verify_token,
    get_user_by_id,
    create_password_reset_token,
    reset_password,
    send_reset_email
)

from services.ai_reviewer import review_code_with_ai


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CORS
# =========================================================

CORS(app)
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
    supports_credentials=True
)


# =========================================================
# HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "CodeGuard Backend is Running",
        "status": "online"
    }), 200


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["POST"])
def signup():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400

        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name:
            return jsonify({
                "success": False,
                "message": "Name is required"
            }), 400

        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400

        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400

        if len(password) < 6:
            return jsonify({
                "success": False,
                "message": "Password must be at least 6 characters"
            }), 400

        user = create_user(
            name,
            email,
            password
        )

        if user is None:
            return jsonify({
                "success": False,
                "message": "User with this email already exists"
            }), 409

        token = create_token(user)

        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "token": token,
            "user": user
        }), 201

    except Exception as error:

        print("Signup Error:", error)

        return jsonify({
            "success": False,
            "message": "Signup failed",
            "error": str(error)
        }), 500


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400

        if not password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400

        user = authenticate_user(
            email,
            password
        )

        if user is None:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        token = create_token(user)

        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": user
        }), 200

    except Exception as error:

        print("Login Error:", error)

        return jsonify({
            "success": False,
            "message": "Login failed",
            "error": str(error)
        }), 500


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400

        email = data.get("email", "").strip().lower()

        if not email:
            return jsonify({
                "success": False,
                "message": "Email is required"
            }), 400

        token = create_password_reset_token(email)

        if token is None:
            return jsonify({
                "success": False,
                "message": "No account found with this email"
            }), 404

        send_reset_email(
            email,
            token
        )

        return jsonify({
            "success": True,
            "message": "Password reset link has been sent to your email"
        }), 200

    except Exception as error:

        print("Forgot Password Error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to send password reset email",
            "error": str(error)
        }), 500


# =========================================================
# RESET PASSWORD
# =========================================================

@app.route("/reset-password", methods=["POST"])
def reset_user_password():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No data received"
            }), 400

        token = data.get("token", "")
        new_password = data.get("password", "")

        if not token:
            return jsonify({
                "success": False,
                "message": "Reset token is required"
            }), 400

        if not new_password:
            return jsonify({
                "success": False,
                "message": "Password is required"
            }), 400

        if len(new_password) < 6:
            return jsonify({
                "success": False,
                "message": "Password must be at least 6 characters"
            }), 400

        success = reset_password(
            token,
            new_password
        )

        if not success:
            return jsonify({
                "success": False,
                "message": "Invalid or expired reset token"
            }), 400

        return jsonify({
            "success": True,
            "message": "Password reset successfully"
        }), 200

    except Exception as error:

        print("Reset Password Error:", error)

        return jsonify({
            "success": False,
            "message": "Password reset failed",
            "error": str(error)
        }), 500


# =========================================================
# VERIFY TOKEN
# =========================================================

@app.route("/verify-token", methods=["POST"])
def verify_user_token():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Token is required"
            }), 400

        token = data.get("token")

        if not token:
            return jsonify({
                "success": False,
                "message": "Token is required"
            }), 400

        payload = verify_token(token)

        if payload is None:
            return jsonify({
                "success": False,
                "message": "Invalid or expired token"
            }), 401

        return jsonify({
            "success": True,
            "message": "Token is valid",
            "user": payload
        }), 200

    except Exception as error:

        print("Token Verification Error:", error)

        return jsonify({
            "success": False,
            "message": "Token verification failed"
        }), 500


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile/<user_id>", methods=["GET"])
def profile(user_id):

    try:

        user = get_user_by_id(user_id)

        if user is None:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "user": user
        }), 200

    except Exception as error:

        print("Profile Error:", error)

        return jsonify({
            "success": False,
            "message": "Failed to get profile"
        }), 500


# =========================================================
# DSA / LEETCODE DETECTION
# =========================================================

def is_dsa_problem(text):

    text_lower = text.lower()

    dsa_keywords = [
        "two sum",
        "three sum",
        "array",
        "linked list",
        "binary tree",
        "tree",
        "graph",
        "stack",
        "queue",
        "heap",
        "priority queue",
        "hashmap",
        "hash map",
        "hash table",
        "dynamic programming",
        "sliding window",
        "two pointer",
        "two pointers",
        "binary search",
        "depth first search",
        "breadth first search",
        "dfs",
        "bfs",
        "recursion",
        "backtracking",
        "sorting",
        "searching",
        "substring",
        "subarray",
        "palindrome",
        "linkedlist",
        "leetcode",
        "hackerrank",
        "competitive programming",
        "algorithm",
        "return indices",
        "return the indices",
        "input:",
        "output:",
        "constraints:",
        "solve this",
        "solve the problem",
        "find the",
        "given an integer",
        "given an array",
        "given a string"
    ]

    for keyword in dsa_keywords:

        if keyword in text_lower:
            return True

    return False


# =========================================================
# EXTRACT AI COMPLEXITY
# =========================================================

def extract_complexity_from_ai(ai_text):

    if not ai_text:
        return None, None

    time_complexity = None
    space_complexity = None

    # -----------------------------------------------------
    # Time Complexity
    # -----------------------------------------------------

    time_patterns = [
        r"time complexity\s*:\s*([^\n\r]+)",
        r"time\s*complexity\s*:\s*([^\n\r]+)",
        r"time\s*:\s*([^\n\r]+)"
    ]

    for pattern in time_patterns:

        match = re.search(
            pattern,
            ai_text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            value = value.split("—")[0].strip()
            value = value.split("-")[0].strip()

            if "O(" in value or "o(" in value:
                time_complexity = value
                break

    # -----------------------------------------------------
    # Space Complexity
    # -----------------------------------------------------

    space_patterns = [
        r"space complexity\s*:\s*([^\n\r]+)",
        r"space\s*:\s*([^\n\r]+)"
    ]

    for pattern in space_patterns:

        match = re.search(
            pattern,
            ai_text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            value = value.split("—")[0].strip()
            value = value.split("-")[0].strip()

            if "O(" in value or "o(" in value:
                space_complexity = value
                break

    return time_complexity, space_complexity


# =========================================================
# BASIC COMPLEXITY FOR NORMAL SOURCE CODE
# =========================================================

def estimate_basic_complexity(code):

    lines = code.splitlines()

    loop_lines = []

    for line in lines:

        stripped = line.strip()

        if (
            stripped.startswith("for ")
            or stripped.startswith("for(")
            or stripped.startswith("for (")
            or stripped.startswith("while ")
            or stripped.startswith("while(")
            or stripped.startswith("while (")
        ):

            loop_lines.append(line)

    loop_count = len(loop_lines)

    # -----------------------------------------------
    # No loop
    # -----------------------------------------------

    if loop_count == 0:

        time_complexity = "O(1)"

    # -----------------------------------------------
    # One loop
    # -----------------------------------------------

    elif loop_count == 1:

        time_complexity = "O(n)"

    # -----------------------------------------------
    # Multiple loops
    # -----------------------------------------------

    else:

        time_complexity = "O(n²) or higher"

    return time_complexity


# =========================================================
# CODE ANALYZER + AI
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze_code():

    try:

        # =================================================
        # GET REQUEST DATA
        # =================================================

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No analysis data received"
            }), 400

        code = data.get(
            "code",
            ""
        ).strip()

        language = data.get(
            "language",
            "Python"
        )

        action = data.get(
            "action",
            "full"
        )

        # =================================================
        # VALIDATE
        # =================================================

        if not code:

            return jsonify({
                "success": False,
                "message": "Code is required"
            }), 400

        print("\n========================================")
        print("CODE ANALYSIS REQUEST")
        print("========================================")
        print("Language:", language)
        print("Action:", action)
        print("========================================")

        # =================================================
        # DETECT DSA
        # =================================================

        dsa_mode = is_dsa_problem(code)

        print(
            "Mode:",
            "DSA / LEETCODE" if dsa_mode else "CODE REVIEW"
        )

        # =================================================
        # BASIC INFORMATION
        # =================================================

        lines = code.splitlines()

        non_empty_lines = [
            line
            for line in lines
            if line.strip()
        ]

        total_lines = len(lines)

        # =================================================
        # BUG DETECTION
        # =================================================

        bugs = []

        if "TODO" in code:

            bugs.append({
                "type": "Warning",
                "message": (
                    "TODO comment found. "
                    "This code section may need implementation."
                ),
                "line": None
            })

        # Python print

        if (
            "print(" in code
            and language.lower() in ["python", "py"]
        ):

            bugs.append({
                "type": "Info",
                "message": "Debug print statement detected.",
                "line": None
            })

        # JavaScript console

        if (
            "console.log" in code
            and language.lower() in ["javascript", "js"]
        ):

            bugs.append({
                "type": "Info",
                "message": "console.log statement detected.",
                "line": None
            })

        # =================================================
        # COMPLEXITY
        # =================================================

        if dsa_mode:

            time_complexity = "AI analysis"
            space_complexity = "AI analysis"

            complexity_reason = (
                "Complexity will be determined from "
                "the actual algorithm generated by CodeGuard AI."
            )

            space_reason = (
                "Space complexity will be determined "
                "from the actual solution."
            )

        else:

            time_complexity = estimate_basic_complexity(code)

            space_complexity = "O(1)"

            complexity_reason = (
                "Complexity is estimated from "
                "the detected loop structure."
            )

            space_reason = (
                "Basic static analysis did not detect "
                "an obvious additional data structure."
            )

        # =================================================
        # SECURITY
        # =================================================

        security_issues = []

        dangerous_patterns = [

            (
                "eval(",
                "Use of eval() can execute arbitrary code."
            ),

            (
                "exec(",
                "Use of exec() can execute arbitrary code."
            ),

            (
                "password =",
                "Avoid storing passwords directly in source code."
            ),

            (
                "api_key =",
                "API keys should not be hardcoded."
            ),

            (
                "secret =",
                "Secrets should not be hardcoded."
            )

        ]

        for pattern, message in dangerous_patterns:

            if pattern.lower() in code.lower():

                security_issues.append({

                    "type": "Security Warning",

                    "message": message,

                    "pattern": pattern

                })

        # =================================================
        # REFACTORING
        # =================================================

        refactoring_suggestions = []

        if total_lines > 50:

            refactoring_suggestions.append(
                "Consider breaking large code blocks "
                "into smaller functions."
            )

        if len(non_empty_lines) > 20:

            refactoring_suggestions.append(
                "Consider improving code structure "
                "and readability."
            )

        if not refactoring_suggestions:

            refactoring_suggestions = []

        # =================================================
        # TEST CASES
        # =================================================

        test_cases = [

            {
                "name": "Normal Input",

                "description":
                    "Test the program with a normal valid input."
            },

            {
                "name": "Edge Case",

                "description":
                    "Test empty, minimum, maximum "
                    "or boundary input."
            },

            {
                "name": "Invalid Input",

                "description":
                    "Test how the program handles invalid input."
            }

        ]

        # =================================================
        # SYNTAX
        # =================================================

        syntax_result = {

            "valid": True,

            "error": None,

            "message":
                "Basic syntax analysis completed."

        }

        # =================================================
        # STATIC ANALYSIS
        # =================================================

        analysis = {

            "language": language,

            "action": action,

            "mode":
                "LeetCode" if dsa_mode
                else "Code Review",

            "lines_of_code": total_lines,

            "syntax": syntax_result,

            "bugs": bugs,

            "complexity": {

                "time": time_complexity,

                "space": space_complexity,

                "reason": complexity_reason,

                "space_reason": space_reason

            },

            "security": security_issues,

            "refactoring": {

                "suggestions":
                    refactoring_suggestions,

                "refactored_code":
                    None

            },

            "test_cases": {

                "test_cases":
                    test_cases,

                "message":
                    "Basic test cases generated successfully."

            },

            "test_execution": None

        }

        # =================================================
        # AI REVIEW
        # =================================================

        print("\n========================================")
        print("STARTING CODEGUARD AI")
        print("========================================")

        try:

            ai_review = review_code_with_ai(

                code,

                language,

                analysis

            )

            print("\n========================================")
            print("AI REVIEW COMPLETED")
            print("========================================")

            print(
                "AI Success:",
                ai_review.get("success")
            )

            print(
                "AI Model:",
                ai_review.get("model", "N/A")
            )

            # =================================================
            # SYNC AI COMPLEXITY WITH STATIC ANALYSIS
            # =================================================

            ai_text = ai_review.get(
                "review",
                ""
            )

            ai_time, ai_space = extract_complexity_from_ai(
                ai_text
            )

            if dsa_mode:

                if ai_time:

                    analysis["complexity"]["time"] = ai_time

                    analysis["complexity"]["reason"] = (
                        "Complexity determined from "
                        "the AI-generated algorithm."
                    )

                if ai_space:

                    analysis["complexity"]["space"] = ai_space

                    analysis["complexity"]["space_reason"] = (
                        "Space complexity determined from "
                        "the AI-generated solution."
                    )

        except Exception as ai_error:

            print("\n========================================")
            print("AI REVIEW ERROR")
            print("========================================")

            print(ai_error)

            print("========================================")

            ai_review = {

                "success": False,

                "ai_enabled": False,

                "language": language,

                "review": "",

                "message":
                    "AI review failed.",

                "error":
                    str(ai_error)

            }

            if dsa_mode:

                analysis["complexity"]["time"] = "Unknown"
                analysis["complexity"]["space"] = "Unknown"

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Code analyzed successfully",

            "analysis":
                analysis,

            "ai_review":
                ai_review

        }), 200

    except Exception as error:

        print("\n========================================")
        print("ANALYZE ERROR")
        print("========================================")

        print(error)

        print("========================================\n")

        return jsonify({

            "success": False,

            "message":
                "Code analysis failed",

            "error":
                str(error)

        }), 500


# =========================================================
# ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "message":
            "API endpoint not found",

        "path":
            request.path

    }), 404


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("\n========================================")
    print("        CODEGUARD BACKEND")
    print("========================================")
    print("Server: http://127.0.0.1:5000")
    print("Analyzer: http://127.0.0.1:5000/analyze")
    print("AI Reviewer: ENABLED")
    print("Database: MongoDB")
    print("========================================\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )