import { useEffect, useState } from "react";

import {
  Code2,
  Mail,
  Lock,
  User,
  Eye,
  EyeOff,
  ArrowLeft
} from "lucide-react";

import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function Auth({ onLogin }) {
  const [mode, setMode] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [resetToken, setResetToken] = useState("");

  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [resetLink, setResetLink] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      setResetToken(token);
      setMode("reset");
    }
  }, []);

  const clearForm = () => {
    setName("");
    setEmail("");
    setPassword("");
    setResetToken("");
    setError("");
    setSuccess("");
    setResetLink("");
    setShowPassword(false);
  };

  const switchMode = () => {
    setMode(mode === "login" ? "signup" : "login");
    clearForm();

    window.history.replaceState(
      {},
      document.title,
      window.location.pathname
    );
  };

  const goToLogin = () => {
    setMode("login");
    clearForm();

    window.history.replaceState(
      {},
      document.title,
      window.location.pathname
    );
  };

  const getBackendError = (data, response) => {
    if (!data) {
      return `Backend returned status ${response.status}.`;
    }

    if (typeof data.detail === "string") {
      return data.detail;
    }

    if (typeof data.message === "string") {
      return data.message;
    }

    if (typeof data.error === "string") {
      return data.error;
    }

    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item) => {
          if (typeof item === "string") {
            return item;
          }

          return item?.msg || "Invalid input.";
        })
        .join(", ");
    }

    return `Request failed with status ${response.status}.`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (mode === "signup" && !name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (!email.trim()) {
      setError("Please enter your email.");
      return;
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }

    if (!password.trim()) {
      setError("Please enter your password.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      const endpoint =
        mode === "signup"
          ? `${API_URL}/signup`
          : `${API_URL}/login`;

      const requestBody =
        mode === "signup"
          ? {
              name: name.trim(),
              email: email.trim().toLowerCase(),
              password: password
            }
          : {
              email: email.trim().toLowerCase(),
              password: password
            };

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json"
        },
        body: JSON.stringify(requestBody)
      });

      const responseText = await response.text();

      let data = {};

      if (responseText) {
        try {
          data = JSON.parse(responseText);
        } catch {
          throw new Error(
            `Backend returned an invalid response. HTTP ${response.status}`
          );
        }
      }

      if (!response.ok) {
        throw new Error(getBackendError(data, response));
      }

      if (data.success === false) {
        throw new Error(getBackendError(data, response));
      }

      if (mode === "signup") {
        setSuccess(
          data.message ||
            "Account created successfully! Please login."
        );

        setMode("login");
        setName("");
        setPassword("");

        return;
      }

      if (!data.token) {
        throw new Error(
          "Login successful but token was not received from backend."
        );
      }

      localStorage.setItem(
        "codeguard_token",
        data.token
      );

      const loggedInUser = {
        id:
          data.user?.id ||
          data.user?._id ||
          "",

        name:
          data.user?.name ||
          email.split("@")[0],

        email:
          data.user?.email ||
          email.trim().toLowerCase(),

        role:
          data.user?.role ||
          "user"
      };

      localStorage.setItem(
        "codeguard_user",
        JSON.stringify(loggedInUser)
      );

      if (typeof onLogin === "function") {
        onLogin(loggedInUser);
      } else {
        throw new Error(
          "Login successful but application could not open."
        );
      }
    } catch (error) {
      console.error(
        "CodeGuard Authentication Error:",
        error
      );

      if (error instanceof TypeError) {
        setError(
          "Cannot connect to backend. Check Render backend or CORS."
        );
      } else {
        setError(
          error.message ||
            "Something went wrong. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");
    setResetLink("");

    if (!email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/forgot-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json"
          },
          body: JSON.stringify({
            email: email.trim().toLowerCase()
          })
        }
      );

      const responseText = await response.text();

      let data = {};

      if (responseText) {
        try {
          data = JSON.parse(responseText);
        } catch {
          throw new Error(
            `Invalid backend response. HTTP ${response.status}`
          );
        }
      }

      if (!response.ok) {
        throw new Error(
          getBackendError(data, response)
        );
      }

      if (data.success === false) {
        throw new Error(
          getBackendError(data, response)
        );
      }

      setSuccess(
        data.message ||
          "If this email is registered, a reset link will be generated."
      );

      if (data.reset_link) {
        setResetLink(data.reset_link);
      }
    } catch (error) {
      console.error(
        "Forgot Password Error:",
        error
      );

      if (error instanceof TypeError) {
        setError("Cannot connect to backend.");
      } else {
        setError(
          error.message ||
            "Something went wrong."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (!resetToken.trim()) {
      setError("Reset token is missing.");
      return;
    }

    if (!password.trim()) {
      setError("Please enter your new password.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/reset-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json"
          },
          body: JSON.stringify({
            token: resetToken,
            new_password: password
          })
        }
      );

      const responseText = await response.text();

      let data = {};

      if (responseText) {
        try {
          data = JSON.parse(responseText);
        } catch {
          throw new Error(
            `Invalid backend response. HTTP ${response.status}`
          );
        }
      }

      if (!response.ok) {
        throw new Error(
          getBackendError(data, response)
        );
      }

      if (data.success === false) {
        throw new Error(
          getBackendError(data, response)
        );
      }

      setSuccess(
        data.message ||
          "Password reset successfully! You can now login."
      );

      setPassword("");
      setResetToken("");

      setTimeout(() => {
        setMode("login");

        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );
      }, 1500);
    } catch (error) {
      console.error(
        "Reset Password Error:",
        error
      );

      if (error instanceof TypeError) {
        setError("Cannot connect to backend.");
      } else {
        setError(
          error.message ||
            "Unable to reset password."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  if (mode === "forgot") {
    return (
      <div className="auth-page">
        <div className="auth-card">

          <div className="auth-logo">
            <div className="auth-logo-icon">
              <Code2 size={25} />
            </div>

            <span>CodeGuard</span>
          </div>

          <h1>Forgot password?</h1>

          <p className="auth-subtitle">
            Enter your email and we'll help you reset your password.
          </p>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          {success && (
            <div
              style={{
                padding: "12px",
                marginBottom: "15px",
                borderRadius: "8px",
                background:
                  "rgba(34, 197, 94, 0.10)",
                color: "#22c55e",
                fontSize: "13px",
                lineHeight: "1.5"
              }}
            >
              {success}
            </div>
          )}

          <form onSubmit={handleForgotPassword}>

            <div className="auth-field">
              <label>Email</label>

              <div className="auth-input-wrapper">
                <Mail size={18} />

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setError("");
                    setSuccess("");
                    setResetLink("");
                  }}
                  autoComplete="email"
                />
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading
                ? "Generating reset link..."
                : "Send Reset Link"}
            </button>

          </form>

          {resetLink && (
            <div
              style={{
                marginTop: "15px",
                padding: "12px",
                borderRadius: "8px",
                background:
                  "rgba(59, 130, 246, 0.10)",
                fontSize: "12px",
                lineHeight: "1.5"
              }}
            >
              <div
                style={{
                  marginBottom: "8px",
                  fontWeight: "600"
                }}
              >
                Development Reset Link
              </div>

              <a
                href={resetLink}
                style={{
                  color: "#60a5fa",
                  wordBreak: "break-all"
                }}
              >
                Open Reset Password
              </a>
            </div>
          )}

          <div
            className="auth-switch"
            style={{
              marginTop: "20px"
            }}
          >
            <button
              type="button"
              onClick={goToLogin}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px"
              }}
            >
              <ArrowLeft size={14} />
              Back to Login
            </button>
          </div>

          <div
            style={{
              marginTop: "25px",
              textAlign: "center",
              fontSize: "11px",
              opacity: 0.5
            }}
          >
            AI-powered code analysis & debugging
          </div>

        </div>
      </div>
    );
  }

  if (mode === "reset") {
    return (
      <div className="auth-page">
        <div className="auth-card">

          <div className="auth-logo">
            <div className="auth-logo-icon">
              <Code2 size={25} />
            </div>

            <span>CodeGuard</span>
          </div>

          <h1>Reset password</h1>

          <p className="auth-subtitle">
            Create a new password for your CodeGuard account.
          </p>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          {success && (
            <div
              style={{
                padding: "12px",
                marginBottom: "15px",
                borderRadius: "8px",
                background:
                  "rgba(34, 197, 94, 0.10)",
                color: "#22c55e",
                fontSize: "13px",
                lineHeight: "1.5"
              }}
            >
              {success}
            </div>
          )}

          <form onSubmit={handleResetPassword}>

            <div className="auth-field">
              <label>New Password</label>

              <div className="auth-input-wrapper">
                <Lock size={18} />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter new password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError("");
                  }}
                  autoComplete="new-password"
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(!showPassword)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword
                    ? <EyeOff size={18} />
                    : <Eye size={18} />
                  }
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading
                ? "Resetting password..."
                : "Reset Password"}
            </button>

          </form>

          <div className="auth-switch">
            <button
              type="button"
              onClick={goToLogin}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px"
              }}
            >
              <ArrowLeft size={14} />
              Back to Login
            </button>
          </div>

          <div
            style={{
              marginTop: "25px",
              textAlign: "center",
              fontSize: "11px",
              opacity: 0.5
            }}
          >
            AI-powered code analysis & debugging
          </div>

        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-logo">

          <div className="auth-logo-icon">
            <Code2 size={25} />
          </div>

          <span>CodeGuard</span>

        </div>

        <h1>
          {mode === "login"
            ? "Welcome back"
            : "Create your account"}
        </h1>

        <p className="auth-subtitle">
          {mode === "login"
            ? "Login to continue to CodeGuard"
            : "Create your CodeGuard account"}
        </p>

        {error && (
          <div className="auth-error">
            {error}
          </div>
        )}

        {success && (
          <div
            style={{
              padding: "12px",
              marginBottom: "15px",
              borderRadius: "8px",
              background:
                "rgba(34, 197, 94, 0.10)",
              color: "#22c55e",
              fontSize: "13px",
              lineHeight: "1.5"
            }}
          >
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit}>

          {mode === "signup" && (
            <div className="auth-field">

              <label>Full Name</label>

              <div className="auth-input-wrapper">

                <User size={18} />

                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value);
                    setError("");
                  }}
                  autoComplete="name"
                />

              </div>

            </div>
          )}

          <div className="auth-field">

            <label>Email</label>

            <div className="auth-input-wrapper">

              <Mail size={18} />

              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError("");
                }}
                autoComplete="email"
              />

            </div>

          </div>

          <div className="auth-field">

            <label>Password</label>

            <div className="auth-input-wrapper">

              <Lock size={18} />

              <input
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError("");
                }}
                autoComplete={
                  mode === "signup"
                    ? "new-password"
                    : "current-password"
                }
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
                aria-label={
                  showPassword
                    ? "Hide password"
                    : "Show password"
                }
              >
                {showPassword
                  ? <EyeOff size={18} />
                  : <Eye size={18} />
                }
              </button>

            </div>

          </div>

          {mode === "login" && (
            <div
              style={{
                textAlign: "right",
                marginTop: "-8px",
                marginBottom: "15px"
              }}
            >
              <button
                type="button"
                onClick={() => {
                  setMode("forgot");
                  setError("");
                  setSuccess("");
                  setPassword("");
                  setResetLink("");
                }}
                style={{
                  background: "none",
                  border: "none",
                  padding: "0",
                  color: "#60a5fa",
                  cursor: "pointer",
                  fontSize: "13px"
                }}
              >
                Forgot password?
              </button>
            </div>
          )}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading
              ? "Please wait..."
              : mode === "login"
                ? "Login"
                : "Create Account"}
          </button>

        </form>

        <div className="auth-switch">

          {mode === "login"
            ? "Don't have an account?"
            : "Already have an account?"}

          <button
            type="button"
            onClick={switchMode}
          >
            {mode === "login"
              ? " Sign up"
              : " Login"}
          </button>

        </div>

        <div
          style={{
            marginTop: "25px",
            textAlign: "center",
            fontSize: "11px",
            opacity: 0.5
          }}
        >
          AI-powered code analysis & debugging
        </div>

      </div>
    </div>
  );
}

export default Auth;