import os
import time
import random

from dotenv import load_dotenv
from google import genai

load_dotenv()

# ==============================
# GEMINI CONFIG
# ==============================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(
    api_key=api_key
)


# ==============================
# MODELS
# ==============================

# Primary model
PRIMARY_MODEL = "gemini-3.8-flash"

# Fallback models
# Agar primary temporarily unavailable ho
FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash"
]


# ==============================
# RETRY SETTINGS
# ==============================

MAX_RETRIES = 3
BASE_DELAY = 2


# ==============================
# CHECK TRANSIENT ERROR
# ==============================

def is_retryable_error(error):
    """
    Check whether Gemini error is temporary.
    """

    error_text = str(error).lower()

    retry_errors = [
        "503",
        "unavailable",
        "high demand",
        "temporarily",
        "429",
        "resource_exhausted",
        "too many requests",
        "500",
        "internal",
        "504",
        "deadline"
    ]

    return any(
        message in error_text
        for message in retry_errors
    )


# ==============================
# GEMINI CALL WITH RETRY
# ==============================

def generate_with_retry(model, prompt):
    """
    Call Gemini with exponential backoff.

    Example:

    Attempt 1
       ↓
      2 sec

    Attempt 2
       ↓
      4 sec

    Attempt 3
       ↓
      8 sec
    """

    last_error = None

    for attempt in range(MAX_RETRIES):

        try:

            print(
                f"[CodeGuard AI] "
                f"Trying {model} "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response and response.text:

                print(
                    f"[CodeGuard AI] "
                    f"{model} response received"
                )

                return response.text

            raise Exception(
                "Gemini returned an empty response."
            )

        except Exception as error:

            last_error = error

            print(
                f"[CodeGuard AI] "
                f"{model} failed: {error}"
            )

            # Non-temporary error
            if not is_retryable_error(error):

                print(
                    "[CodeGuard AI] "
                    "Non-retryable error."
                )

                break

            # Last attempt
            if attempt == MAX_RETRIES - 1:
                break

            # Exponential backoff
            delay = BASE_DELAY * (2 ** attempt)

            # Small random jitter
            jitter = random.uniform(0, 1)

            total_delay = delay + jitter

            print(
                f"[CodeGuard AI] "
                f"Retrying in {total_delay:.1f} seconds..."
            )

            time.sleep(total_delay)

    raise last_error


# ==============================
# BUILD AI PROMPT
# ==============================

def build_prompt(code, language, analysis):

    prompt = f"""
You are CodeGuard AI.

You are an expert programming assistant.

The user may give you either:

1. Normal source code that needs debugging/review.
OR
2. A LeetCode / DSA problem that needs to be solved.

You MUST first understand what the user has provided.

==================================================
IMPORTANT MODE DETECTION
==================================================

If the input contains:

- LeetCode problem
- DSA question
- Algorithm question
- Array/string/linked list/tree/graph problem
- Input/output examples
- "solve this"
- "give solution"
- competitive programming problem

then treat it as:

Mode: LeetCode

Otherwise treat it as:

Mode: Code Review

==================================================
IF MODE IS LEETCODE
==================================================

Solve the problem in {language}.

Give:

Mode: LeetCode

Problem:
Short problem understanding.

Approach:
Explain the algorithm simply.

Steps:
1. ...
2. ...
3. ...

Time Complexity:
O(...)

Space Complexity:
O(...)

Solution Code:
Provide complete working code.

The code should be suitable for LeetCode-style submission.

Do NOT give unnecessarily complicated code.

==================================================
IF MODE IS CODE REVIEW
==================================================

Review the provided source code.

Find:

- Syntax bugs
- Logic bugs
- Runtime errors
- Security issues
- Performance problems
- Bad practices
- Possible improvements

Explain everything in simple language.

Return:

Mode: Code Review

Summary:
...

Risk Level:
Low / Medium / High

Issues:

1. Issue:
   Line:
   Explanation:
   Fix:

2. Issue:
   Line:
   Explanation:
   Fix:

Good Things:
- ...
- ...

Improved Code:
If the code has problems, provide the complete corrected code.

If no changes are required, say:

No changes required.

==================================================
STATIC ANALYSIS
==================================================

{analysis}

==================================================
PROGRAMMING LANGUAGE
==================================================

{language}

==================================================
USER INPUT
==================================================

{code}

==================================================
IMPORTANT
==================================================

Always provide useful output.

For LeetCode:
Give complete solution code.

For normal code:
Give corrected code when necessary.

Do not invent errors that do not exist.
"""

    return prompt


# ==============================
# MAIN AI REVIEW FUNCTION
# ==============================

def review_code_with_ai(code, language, analysis):

    prompt = build_prompt(
        code,
        language,
        analysis
    )

    # ==========================================
    # TRY PRIMARY MODEL
    # ==========================================

    try:

        review = generate_with_retry(
            PRIMARY_MODEL,
            prompt
        )

        return {
            "success": True,
            "ai_enabled": True,
            "model": PRIMARY_MODEL,
            "language": language,
            "review": review,
            "message": "AI review completed successfully."
        }

    except Exception as primary_error:

        print(
            "[CodeGuard AI] "
            "Primary model failed."
        )

        print(primary_error)

    # ==========================================
    # TRY FALLBACK MODELS
    # ==========================================

    for fallback_model in FALLBACK_MODELS:

        try:

            print(
                f"[CodeGuard AI] "
                f"Trying fallback model: {fallback_model}"
            )

            review = generate_with_retry(
                fallback_model,
                prompt
            )

            return {
                "success": True,
                "ai_enabled": True,
                "model": fallback_model,
                "language": language,
                "review": review,
                "message": (
                    "AI review completed using fallback model."
                )
            }

        except Exception as fallback_error:

            print(
                f"[CodeGuard AI] "
                f"Fallback model failed: "
                f"{fallback_error}"
            )

    # ==========================================
    # ALL MODELS FAILED
    # ==========================================

    return {
        "success": False,
        "ai_enabled": False,
        "language": language,
        "review": "",
        "message": (
            "Gemini AI is temporarily unavailable. "
            "Please try again after a short while."
        )
    }