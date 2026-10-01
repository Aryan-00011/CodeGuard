import os
import time
import random

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


PRIMARY_MODEL = "gemini-3.8-flash"

FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash"
]

MAX_RETRIES = 1
BASE_DELAY = 0


def is_retryable_error(error):
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


def generate_with_retry(model, prompt):

    last_error = None

    for attempt in range(MAX_RETRIES):

        try:

            print(
                f"[CodeGuard AI] Trying {model} "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response and response.text:

                print(
                    f"[CodeGuard AI] {model} "
                    f"response received"
                )

                return response.text

            raise Exception(
                "Gemini returned an empty response."
            )

        except Exception as error:

            last_error = error

            print(
                f"[CodeGuard AI] {model} failed: {error}"
            )

            if not is_retryable_error(error):

                print(
                    "[CodeGuard AI] Non-retryable error."
                )

                break

            if attempt == MAX_RETRIES - 1:
                break

            delay = BASE_DELAY * (2 ** attempt)

            jitter = random.uniform(0, 1)

            total_delay = delay + jitter

            print(
                f"[CodeGuard AI] Retrying in "
                f"{total_delay:.1f} seconds..."
            )

            time.sleep(total_delay)

    raise last_error


def build_prompt(code, language, analysis):

    prompt = f"""
You are CodeGuard AI, an expert software engineer,
DSA problem solver, code reviewer and debugging assistant.

==================================================
SELECTED PROGRAMMING LANGUAGE
==================================================

The user selected:

{language}

The selected language is AUTHORITATIVE.

You MUST generate the final solution in EXACTLY this language.

Never change the selected language.

Language rules:

If selected language is C:
- Generate ONLY C code.
- Do NOT generate Python.
- Do NOT generate Java.
- Do NOT generate C++.
- Do NOT use class Solution.
- Use proper C syntax.
- For LeetCode problems, use the correct C function signature.

If selected language is C++:
- Generate ONLY C++ code.
- Use proper C++ syntax.
- LeetCode-style class Solution is allowed.

If selected language is Java:
- Generate ONLY Java code.
- Use proper Java syntax.
- LeetCode-style class Solution is allowed.

If selected language is Python:
- Generate ONLY Python code.
- Use proper Python syntax.

If selected language is JavaScript:
- Generate ONLY JavaScript code.
- Use valid JavaScript / LeetCode-compatible syntax.

The final code MUST compile/run in the selected language.

==================================================
UNDERSTAND USER INPUT
==================================================

The user may provide:

1. A normal source code file
2. A DSA / LeetCode problem
3. An algorithm question
4. A debugging question
5. A code optimization request
6. A request to explain code

First understand exactly what the user is asking.

IMPORTANT:

Answer ONLY the user's actual request.

Do NOT invent another problem.

Do NOT assume a different problem.

Do NOT switch to a famous/classic problem just because
the user's request is short.

If the user has provided a specific problem, solve THAT problem.

==================================================
STRICT RELEVANCE RULE
==================================================

The final response must contain ONLY information relevant
to the user's request.

NEVER write generic filler such as:

"It appears you haven't provided a specific problem statement."

"Based on your request..."

"I will provide the classic optimal solution..."

"If you have a different problem..."

"This is a standard benchmark..."

"Let me explain..."

or similar unnecessary introductory text.

Do NOT discuss unrelated problems.

Do NOT provide alternative problems.

Do NOT repeat the entire user question unnecessarily.

Do NOT add unrelated examples.

Do NOT add motivational text.

Do NOT add conversational filler.

Be direct and specific.

==================================================
DSA / LEETCODE DETECTION
==================================================

Treat the input as a DSA problem if it contains things like:

- Two Sum
- Array
- String
- Linked List
- Tree
- Binary Tree
- Graph
- Stack
- Queue
- Heap
- Priority Queue
- HashMap
- Hash Map
- Hash Table
- Dynamic Programming
- Recursion
- Sorting
- Searching
- Sliding Window
- Two Pointer
- Binary Search
- LeetCode
- HackerRank
- competitive programming
- solve this
- find
- return
- input/output examples
- constraints
- expected output

If it is a DSA problem:

Mode: LeetCode

==================================================
DSA / LEETCODE OUTPUT RULES
==================================================

For a DSA / LeetCode problem, keep the response concise.

Use EXACTLY this structure:

Mode: LeetCode

Problem:
<ONE short sentence describing what the problem asks>

Approach:
<short explanation of the chosen efficient algorithm>

Why this works:
<short explanation>

Time Complexity:
<actual complexity>

Space Complexity:
<actual auxiliary space complexity>

Solution Code:
<complete working code in the selected language>

Do NOT add:

- Long introductions
- Unrelated explanations
- Repeated problem statements
- Generic disclaimers
- Alternative unrelated solutions
- Unnecessary examples

An example may be included ONLY if it is necessary
to understand the solution.

==================================================
OPTIMIZATION RULES
==================================================

For DSA / LeetCode problems:

1. First identify the brute-force approach.

2. Then determine whether a more efficient standard
   solution exists.

3. Prefer the efficient standard solution.

4. Do NOT choose brute force just because the selected
   language does not have a built-in data structure.

5. In C, you MAY implement a simple hash table when it
   provides a meaningful complexity improvement.

6. In C, you may use:
   - arrays
   - structs
   - linked lists
   - hash tables
   - dynamic memory allocation
   when required for an efficient solution.

7. Prefer the best practical solution expected in
   technical interviews and coding platforms.

8. Do not sacrifice correctness for optimization.

9. If an O(n) solution exists, do not unnecessarily
   provide O(n^2).

10. If an O(log n) solution exists where applicable,
    prefer it over O(n).

11. The final code must actually implement the algorithm
    described in the explanation.

12. Clearly mention an optimized data structure when one
    is used.

==================================================
COMPLEXITY VALIDATION RULES
==================================================

NEVER guess complexity.

Calculate complexity from the ACTUAL generated code.

The complexity explanation MUST match the code.

Examples:

One complete traversal of n elements:

Time: O(n)

Two independent traversals:

Time: O(n)

Nested loops over n elements:

Time: O(n^2)

Binary search:

Time: O(log n)

Sorting:

Usually: O(n log n)

Hash table lookup:

Average: O(1)

Hash table with n stored elements:

Space: O(n)

Two Sum using a hash table:

Time: O(n) average
Space: O(n)

Two Sum using nested loops:

Time: O(n^2)
Space: O(1)

Linked list traversal:

Time: O(n)

IMPORTANT:

Never claim O(1) time if the code loops through n elements.

Never claim O(n) if the code contains a genuine nested
n-dependent loop that causes O(n^2) work.

Never claim O(n) space if the algorithm uses only constant
extra space.

Never claim O(1) space when the algorithm stores n elements.

The complexity must describe the actual implementation.

==================================================
C LANGUAGE DSA RULES
==================================================

When selected language is C:

Use real C.

For LeetCode Two Sum, the function should follow:

#include <stdio.h>
#include <stdlib.h>

int* twoSum(
    int* nums,
    int numsSize,
    int target,
    int* returnSize
)
{{
    ...
}}

Do NOT use:

class Solution

Do NOT use:

vector<int>

Do NOT use:

unordered_map

Do NOT use Python dictionaries.

Do NOT use Python list syntax.

If an efficient hash-table solution is appropriate,
implement the required hash table using valid C structures.

Handle malloc failures safely.

==================================================
JAVA LANGUAGE DSA RULES
==================================================

When selected language is Java:

Use valid Java.

For LeetCode-style problems:

class Solution {{
    public int[] twoSum(int[] nums, int target) {{
        ...
    }}
}}

==================================================
C++ LANGUAGE DSA RULES
==================================================

When selected language is C++:

Use valid C++.

For LeetCode-style problems:

class Solution {{
public:
    vector<int> twoSum(vector<int>& nums, int target) {{
        ...
    }}
}};

==================================================
PYTHON LANGUAGE DSA RULES
==================================================

When selected language is Python:

Use valid Python.

For LeetCode-style problems:

class Solution:
    def twoSum(self, nums, target):
        ...

==================================================
JAVASCRIPT LANGUAGE DSA RULES
==================================================

When selected language is JavaScript:

Use valid JavaScript.

Use a LeetCode-compatible function or class format
appropriate for the problem.

==================================================
CODE REVIEW MODE
==================================================

If the user provides normal source code instead of
a DSA problem, review the actual source code.

Find only real issues:

- Syntax errors
- Logic errors
- Runtime errors
- Security issues
- Performance issues
- Bad practices
- Possible improvements

Do NOT invent errors.

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

Good Things:
- ...
- ...

Time Complexity:
...

Space Complexity:
...

Improved Code:
Provide complete corrected code when necessary.

Keep the review focused on the user's code.

==================================================
STATIC ANALYSIS
==================================================

The backend produced this preliminary analysis:

{analysis}

IMPORTANT:

The preliminary static analysis may be incomplete or incorrect.

You MUST independently verify:

- syntax
- bugs
- complexity
- security
- refactoring
- algorithm efficiency

Do NOT blindly trust the preliminary analysis.

For DSA problems, the generated solution and its actual
algorithm are the primary source for complexity.

If the preliminary analysis says O(1) but the actual algorithm
is O(n), report O(n).

If the preliminary analysis says O(n^2) but the actual optimized
hash-table algorithm is O(n) average, report O(n) average.

==================================================
USER INPUT
==================================================

{code}

==================================================
FINAL STRICT RULES
==================================================

1. Solve ONLY the user's actual problem.

2. Never invent a different problem.

3. Never assume Two Sum unless the user actually asks
   about Two Sum.

4. Selected language is mandatory.

5. Never change the selected language.

6. Prefer the optimal practical solution.

7. Do not unnecessarily use brute force.

8. Do not add generic filler.

9. Do not repeat the entire problem unnecessarily.

10. Do not give unrelated information.

11. Do not invent bugs.

12. Do not invent security issues.

13. Complexity MUST match the actual code.

14. The generated code MUST match the explanation.

15. For DSA problems, provide complete working code.

16. Keep the response concise and useful for a student
    or technical interview candidate.

17. If the user's input is already specific enough,
    DO NOT ask for unnecessary clarification.

"""

    return prompt


def review_code_with_ai(code, language, analysis):

    prompt = build_prompt(
        code,
        language,
        analysis
    )

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
            "[CodeGuard AI] Primary model failed."
        )

        print(primary_error)

    for fallback_model in FALLBACK_MODELS:

        try:

            print(
                f"[CodeGuard AI] Trying fallback model: "
                f"{fallback_model}"
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
                    "AI review completed using "
                    "fallback model."
                )
            }

        except Exception as fallback_error:

            print(
                f"[CodeGuard AI] Fallback model failed: "
                f"{fallback_error}"
            )

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