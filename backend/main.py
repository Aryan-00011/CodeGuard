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

app = FastAPI(
    title="CodeGuard API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://code-guard-umber.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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


@app.get("/")
def home():
    return {
        "success": True,
        "message": "CodeGuard Backend is running",
        "version": "2.0.0"
    }


@app.post("/signup")
def signup(request: SignupRequest):
    try:
        if not request.name.strip():
            return {
                "success": False,
                "message": "Name is required."
            }

        if len(request.password) < 6:
            return {
                "success": False,
                "message": "Password must be at least 6 characters."
            }

        user = create_user(
            name=request.name.strip(),
            email=str(request.email).lower().strip(),
            password=request.password
        )

        if user is None:
            return {
                "success": False,
                "message": "Email already registered."
            }

        print("New user registered:", user["email"])
        print("Role:", user["role"])

        return {
            "success": True,
            "message": "Account created successfully.",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }

    except Exception as error:
        print("SIGNUP ERROR:", error)

        return {
            "success": False,
            "message": str(error)
        }


@app.post("/login")
def login(request: LoginRequest):
    try:
        user = authenticate_user(
            email=str(request.email).lower().strip(),
            password=request.password
        )

        if user is None:
            return {
                "success": False,
                "message": "Incorrect email or password."
            }

        token = create_token(user)

        print("User logged in:", user["email"])
        print("Role:", user["role"])

        return {
            "success": True,
            "message": "Login successful.",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }

    except Exception as error:
        print("LOGIN ERROR:", error)

        return {
            "success": False,
            "message": str(error)
        }


@app.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest):
    try:
        email = str(request.email).lower().strip()

        reset_token = create_password_reset_token(email)

        if reset_token is None:
            return {
                "success": True,
                "message": "If this email is registered, a password reset link will be generated."
            }

        reset_link = (
            "https://code-guard-umber.vercel.app/"
            "?token="
            + reset_token
        )

        print("PASSWORD RESET REQUEST")
        print("Email:", email)
        print("Reset link:", reset_link)
        print("Token expires in 15 minutes.")

        return {
            "success": True,
            "message": "Password reset link generated.",
            "reset_link": reset_link
        }

    except Exception as error:
        print("FORGOT PASSWORD ERROR:", error)

        return {
            "success": False,
            "message": str(error)
        }


@app.post("/reset-password")
def reset_password_route(request: ResetPasswordRequest):
    try:
        token = request.token.strip()

        if not token:
            return {
                "success": False,
                "message": "Reset token is required."
            }

        if len(request.new_password) < 6:
            return {
                "success": False,
                "message": "Password must be at least 6 characters."
            }

        success = reset_password(
            token,
            request.new_password
        )

        if not success:
            return {
                "success": False,
                "message": "Reset link is invalid or expired."
            }

        print("PASSWORD RESET SUCCESSFUL")

        return {
            "success": True,
            "message": "Password reset successfully. You can now login."
        }

    except Exception as error:
        print("RESET PASSWORD ERROR:", error)

        return {
            "success": False,
            "message": str(error)
        }


@app.get("/me")
def get_current_user(
    authorization: str | None = Header(default=None)
):
    if not authorization:
        return {
            "success": False,
            "message": "Authorization token is required."
        }

    if not authorization.startswith("Bearer "):
        return {
            "success": False,
            "message": "Invalid authorization format."
        }

    token = authorization.replace(
        "Bearer ",
        "",
        1
    ).strip()

    payload = verify_token(token)

    if payload is None:
        return {
            "success": False,
            "message": "Invalid or expired token."
        }

    return {
        "success": True,
        "user": {
            "id": payload.get("user_id"),
            "name": payload.get("name"),
            "email": payload.get("email"),
            "role": payload.get("role", "user")
        }
    }


class CodeRequest(BaseModel):
    code: str
    language: str
    action: str = "full"


@app.post("/analyze")
def analyze_code(request: CodeRequest):
    try:
        from analyzer.python_analyzer import analyze_python_code
        from analyzer.security import check_security
        from analyzer.refactor import refactor_python_code
        from analyzer.test_generator import generate_test_cases
        from analyzer.test_executor import execute_python_tests
        from services.language_router import analyze_by_language
        from services.ai_reviewer import review_code_with_ai

        if request.language == "Python":
            analysis = analyze_python_code(
                request.code
            )

            analysis["security"] = check_security(
                request.code
            )

            analysis["refactoring"] = refactor_python_code(
                request.code
            )

            analysis["test_cases"] = generate_test_cases(
                request.code
            )

            analysis["test_execution"] = execute_python_tests(
                request.code
            )

        else:
            analysis = analyze_by_language(
                request.code,
                request.language
            )

        ai_review = review_code_with_ai(
            request.code,
            request.language,
            analysis
        )

        return {
            "success": True,
            "language": request.language,
            "analysis": analysis,
            "ai_review": ai_review
        }

    except Exception as error:
        print("ANALYZE ERROR:", error)

        return {
            "success": False,
            "message": str(error)
        }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "service": "CodeGuard Backend"
    }