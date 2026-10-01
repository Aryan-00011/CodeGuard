from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import bcrypt
import jwt
from dotenv import load_dotenv

from database import users_collection


load_dotenv()


SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "codeguard_super_secret_key_change_this"
)

ALGORITHM = "HS256"

TOKEN_EXPIRE_HOURS = 24

RESET_TOKEN_EXPIRE_MINUTES = 15

MAIL_USERNAME = os.getenv("MAIL_USERNAME")

MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


def get_current_time():
    return datetime.now(timezone.utc)


def create_user(name, email, password):

    name = name.strip()

    email = email.lower().strip()

    existing_user = users_collection.find_one({
        "email": email
    })

    if existing_user:
        return None

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = {
        "name": name,
        "email": email,
        "password_hash": hashed_password,
        "role": "user",
        "created_at": get_current_time(),
        "last_login": None,
        "login_count": 0
    }

    result = users_collection.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "name": name,
        "email": email,
        "role": "user"
    }


def authenticate_user(email, password):

    email = email.lower().strip()

    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return None

    stored_password = user.get("password_hash")

    if not stored_password:
        return None

    try:

        password_match = bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password.encode("utf-8")
        )

    except Exception:

        return None

    if not password_match:
        return None

    role = user.get("role", "user")

    login_count = user.get("login_count", 0) + 1

    users_collection.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": {
                "last_login": get_current_time(),
                "login_count": login_count,
                "role": role
            }
        }
    )

    return {
        "id": str(user["_id"]),
        "name": user.get("name", "User"),
        "email": user.get("email", email),
        "role": role
    }


def create_token(user):

    expire = (
        datetime.now(timezone.utc)
        + timedelta(hours=TOKEN_EXPIRE_HOURS)
    )

    payload = {
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "user"),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        return None

    except jwt.InvalidTokenError:

        return None

    except Exception:

        return None


def is_owner(user):

    if not user:
        return False

    return user.get("role", "user") == "owner"


def get_user_by_id(user_id):

    try:

        from bson import ObjectId

        user = users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:
            return None

        return {
            "id": str(user["_id"]),
            "name": user.get("name", "User"),
            "email": user.get("email", ""),
            "role": user.get("role", "user"),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login"),
            "login_count": user.get("login_count", 0)
        }

    except Exception:

        return None


def send_reset_email(email, token):

    if not MAIL_USERNAME or not MAIL_PASSWORD:

        raise Exception(
            "Gmail SMTP credentials are not configured in .env"
        )

    reset_link = (
        f"{FRONTEND_URL}/reset-password?token={token}"
    )

    message = MIMEMultipart("alternative")

    message["Subject"] = "CodeGuard - Reset Your Password"

    message["From"] = MAIL_USERNAME

    message["To"] = email

    text_content = f"""
Hello,

We received a request to reset your CodeGuard password.

Use the following link to reset your password:

{reset_link}

This link will expire in {RESET_TOKEN_EXPIRE_MINUTES} minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
CodeGuard Team
"""

    html_content = f"""
<html>
<body>

<h2>CodeGuard Password Reset</h2>

<p>Hello,</p>

<p>
We received a request to reset your CodeGuard password.
</p>

<p>
Click the button below to reset your password:
</p>

<p>
<a href="{reset_link}"
style="
display:inline-block;
padding:12px 20px;
background:#2563eb;
color:white;
text-decoration:none;
border-radius:6px;
">
Reset Password
</a>
</p>

<p>
Or copy this link into your browser:
</p>

<p>
{reset_link}
</p>

<p>
This link will expire in {RESET_TOKEN_EXPIRE_MINUTES} minutes.
</p>

<p>
If you did not request a password reset, you can safely ignore this email.
</p>

<p>
Regards,<br>
CodeGuard Team
</p>

</body>
</html>
"""

    text_part = MIMEText(
        text_content,
        "plain"
    )

    html_part = MIMEText(
        html_content,
        "html"
    )

    message.attach(text_part)

    message.attach(html_part)

    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        server.login(
            MAIL_USERNAME,
            MAIL_PASSWORD
        )

        server.sendmail(
            MAIL_USERNAME,
            email,
            message.as_string()
        )


def create_password_reset_token(email):

    email = email.lower().strip()

    user = users_collection.find_one({
        "email": email
    })

    if not user:
        return None

    raw_token = secrets.token_urlsafe(48)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    expires_at = (
        get_current_time()
        + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    )

    users_collection.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": {
                "reset_token_hash": token_hash,
                "reset_token_expires": expires_at
            }
        }
    )

    return raw_token


def reset_password(token, new_password):

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    user = users_collection.find_one({
        "reset_token_hash": token_hash
    })

    if not user:
        return False

    expires_at = user.get(
        "reset_token_expires"
    )

    if not expires_at:
        return False

    current_time = get_current_time()

    if expires_at < current_time:

        users_collection.update_one(
            {
                "_id": user["_id"]
            },
            {
                "$unset": {
                    "reset_token_hash": "",
                    "reset_token_expires": ""
                }
            }
        )

        return False

    hashed_password = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    users_collection.update_one(
        {
            "_id": user["_id"]
        },
        {
            "$set": {
                "password_hash": hashed_password
            },
            "$unset": {
                "reset_token_hash": "",
                "reset_token_expires": ""
            }
        }
    )

    return True