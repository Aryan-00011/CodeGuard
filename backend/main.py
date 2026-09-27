from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database import users_collection, chats_collection

from auth import (
    create_user,
    authenticate_user,
    create_token,
    verify_token,
    create_password_reset_token,
    reset_password
)


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="CodeGuard API",
    version="2.0.0"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =====================================================
# AUTH MODELS
# =====================================================

class SignupRequest(BaseModel):

    name: str

    email: EmailStr

    password: str


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class ForgotPasswordRequest(BaseModel):

    email: EmailStr


class ResetPasswordRequest(BaseModel):

    token: str

    new_password: str


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {

        "success": True,

        "message": "CodeGuard Backend is running",

        "version": "2.0.0"

    }


# =====================================================
# SIGNUP
# =====================================================

@app.post("/signup")
def signup(request: SignupRequest):

    try:

        # -------------------------------------------------
        # VALIDATE NAME
        # -------------------------------------------------

        if not request.name.strip():

            return {

                "success": False,

                "message": "Name is required."

            }


        # -------------------------------------------------
        # VALIDATE PASSWORD
        # -------------------------------------------------

        if len(request.password) < 6:

            return {

                "success": False,

                "message":
                    "Password must be at least 6 characters."

            }


        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = create_user(

            name=request.name,

            email=str(request.email),

            password=request.password

        )


        # -------------------------------------------------
        # EMAIL ALREADY EXISTS
        # -------------------------------------------------

        if user is None:

            return {

                "success": False,

                "message":
                    "Email already registered."

            }


        # -------------------------------------------------
        # TERMINAL LOG
        # -------------------------------------------------

        print(
            "================================"
        )

        print(
            f"New user registered: {user['email']}"
        )

        print(
            f"Role: {user['role']}"
        )

        print(
            "================================"
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "Account created successfully.",

            "user": {

                "id": user["id"],

                "name": user["name"],

                "email": user["email"],

                "role": user["role"]

            }

        }


    except Exception as error:

        print(
            "SIGNUP ERROR:",
            error
        )

        return {

            "success": False,

            "message":
                "Unable to create account."

        }


# =====================================================
# LOGIN
# =====================================================

@app.post("/login")
def login(request: LoginRequest):

    try:

        # -------------------------------------------------
        # AUTHENTICATE USER
        # -------------------------------------------------

        user = authenticate_user(

            email=str(request.email),

            password=request.password

        )


        # -------------------------------------------------
        # INVALID LOGIN
        # -------------------------------------------------

        if user is None:

            return {

                "success": False,

                "message":
                    "Incorrect email or password."

            }


        # -------------------------------------------------
        # CREATE JWT TOKEN
        # -------------------------------------------------

        token = create_token(
            user
        )


        # -------------------------------------------------
        # TERMINAL LOG
        # -------------------------------------------------

        print(
            "================================"
        )

        print(
            f"User logged in: {user['email']}"
        )

        print(
            f"Role: {user['role']}"
        )

        print(
            "================================"
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "Login successful.",

            "token": token,

            "user": {

                "id": user["id"],

                "name": user["name"],

                "email": user["email"],

                "role": user["role"]

            }

        }


    except Exception as error:

        print(
            "LOGIN ERROR:",
            error
        )

        return {

            "success": False,

            "message":
                "Login failed."

        }


# =====================================================
# FORGOT PASSWORD
# =====================================================

@app.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest
):

    try:

        # -------------------------------------------------
        # CLEAN EMAIL
        # -------------------------------------------------

        email = str(
            request.email
        ).lower().strip()


        print(
            "================================"
        )

        print(
            "FORGOT PASSWORD REQUEST"
        )

        print(
            f"Email: {email}"
        )

        print(
            "================================"
        )


        # -------------------------------------------------
        # CREATE RESET TOKEN
        # -------------------------------------------------

        reset_token = create_password_reset_token(
            email
        )


        # -------------------------------------------------
        # EMAIL NOT FOUND
        # -------------------------------------------------

        if reset_token is None:

            # We intentionally don't reveal
            # whether an email exists.

            print(
                "No matching user found."
            )

            return {

                "success": True,

                "message":
                    "If this email is registered, "
                    "a password reset link will be generated."

            }


        # -------------------------------------------------
        # DEVELOPMENT RESET LINK
        # -------------------------------------------------
        #
        # IMPORTANT:
        #
        # This is for LOCAL DEVELOPMENT.
        #
        # Later we will send this link through
        # Gmail / SMTP.
        #

        reset_link = (

            "http://127.0.0.1:5173/"
            "reset-password?token="
            + reset_token

        )


        # -------------------------------------------------
        # SHOW RESET LINK IN TERMINAL
        # -------------------------------------------------

        print(
            "================================"
        )

        print(
            "PASSWORD RESET REQUEST"
        )

        print(
            f"Email: {email}"
        )

        print(
            "Reset link:"
        )

        print(
            reset_link
        )

        print(
            "Token expires in 15 minutes."
        )

        print(
            "================================"
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "Password reset link generated.",

            "reset_link":
                reset_link

        }


    except Exception as error:

        print(
            "================================"
        )

        print(
            "FORGOT PASSWORD ERROR:"
        )

        print(
            error
        )

        print(
            "================================"
        )


        return {

            "success": False,

            "message":
                "Unable to process password reset."

        }


# =====================================================
# RESET PASSWORD
# =====================================================

@app.post("/reset-password")
def reset_password_route(
    request: ResetPasswordRequest
):

    try:

        # -------------------------------------------------
        # CHECK TOKEN
        # -------------------------------------------------

        token = request.token.strip()


        if not token:

            return {

                "success": False,

                "message":
                    "Reset token is required."

            }


        # -------------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------------

        if len(request.new_password) < 6:

            return {

                "success": False,

                "message":
                    "Password must be at least 6 characters."

            }


        # -------------------------------------------------
        # RESET PASSWORD
        # -------------------------------------------------

        success = reset_password(

            token,

            request.new_password

        )


        # -------------------------------------------------
        # INVALID / EXPIRED TOKEN
        # -------------------------------------------------

        if not success:

            return {

                "success": False,

                "message":
                    "Reset link is invalid or expired."

            }


        # -------------------------------------------------
        # SUCCESS LOG
        # -------------------------------------------------

        print(
            "================================"
        )

        print(
            "PASSWORD RESET SUCCESSFUL"
        )

        print(
            "================================"
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "Password reset successfully. "
                "You can now login."

        }


    except Exception as error:

        print(
            "================================"
        )

        print(
            "RESET PASSWORD ERROR:"
        )

        print(
            error
        )

        print(
            "================================"
        )


        return {

            "success": False,

            "message":
                "Unable to reset password."

        }


# =====================================================
# GET CURRENT USER
# =====================================================

@app.get("/me")
def get_current_user(
    authorization: str | None = Header(default=None)
):

    # -------------------------------------------------
    # CHECK AUTHORIZATION
    # -------------------------------------------------

    if not authorization:

        return {

            "success": False,

            "message":
                "Authorization token is required."

        }


    # -------------------------------------------------
    # CHECK BEARER TOKEN
    # -------------------------------------------------

    if not authorization.startswith("Bearer "):

        return {

            "success": False,

            "message":
                "Invalid authorization format."

        }


    # -------------------------------------------------
    # EXTRACT TOKEN
    # -------------------------------------------------

    token = authorization.replace(

        "Bearer ",

        "",

        1

    ).strip()


    # -------------------------------------------------
    # VERIFY TOKEN
    # -------------------------------------------------

    payload = verify_token(
        token
    )


    if payload is None:

        return {

            "success": False,

            "message":
                "Invalid or expired token."

        }


    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------

    return {

        "success": True,

        "user": {

            "id": payload.get(
                "user_id"
            ),

            "name": payload.get(
                "name"
            ),

            "email": payload.get(
                "email"
            ),

            "role": payload.get(
                "role",
                "user"
            )

        }

    }


# =====================================================
# CODE REQUEST MODEL
# =====================================================

class CodeRequest(BaseModel):

    code: str

    language: str

    action: str = "full"


# =====================================================
# ANALYZE CODE
# =====================================================

@app.post("/analyze")
def analyze_code(request: CodeRequest):

    try:

        # =============================================
        # IMPORT ANALYZER MODULES
        # =============================================

        from analyzer.python_analyzer import (
            analyze_python_code
        )

        from analyzer.security import (
            check_security
        )

        from analyzer.refactor import (
            refactor_python_code
        )

        from analyzer.test_generator import (
            generate_test_cases
        )

        from analyzer.test_executor import (
            execute_python_tests
        )

        from services.language_router import (
            analyze_by_language
        )

        from services.ai_reviewer import (
            review_code_with_ai
        )


        # =============================================
        # PYTHON ANALYSIS
        # =============================================

        if request.language == "Python":

            analysis = analyze_python_code(
                request.code
            )


            # -------------------------------------------------
            # SECURITY
            # -------------------------------------------------

            analysis["security"] = check_security(
                request.code
            )


            # -------------------------------------------------
            # REFACTORING
            # -------------------------------------------------

            analysis["refactoring"] = (
                refactor_python_code(
                    request.code
                )
            )


            # -------------------------------------------------
            # TEST CASES
            # -------------------------------------------------

            analysis["test_cases"] = (
                generate_test_cases(
                    request.code
                )
            )


            # -------------------------------------------------
            # TEST EXECUTION
            # -------------------------------------------------

            analysis["test_execution"] = (
                execute_python_tests(
                    request.code
                )
            )


        # =============================================
        # OTHER LANGUAGES
        # =============================================

        else:

            analysis = analyze_by_language(

                request.code,

                request.language

            )


        # =============================================
        # AI REVIEW
        # =============================================

        ai_review = review_code_with_ai(

            request.code,

            request.language,

            analysis

        )


        # =============================================
        # RESPONSE
        # =============================================

        return {

            "success": True,

            "language": request.language,

            "analysis": analysis,

            "ai_review": ai_review

        }


    except Exception as error:

        print(
            "ANALYZE ERROR:",
            error
        )

        return {

            "success": False,

            "message":
                str(error)

        }


# =====================================================
# SERVER STATUS
# =====================================================

@app.get("/health")
def health_check():

    return {

        "success": True,

        "status": "healthy",

        "service":
            "CodeGuard Backend"

    }