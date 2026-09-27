from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import os

import bcrypt
import jwt
from dotenv import load_dotenv

from database import users_collection


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# JWT SETTINGS
# =====================================================

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "codeguard_super_secret_key_change_this"
)

ALGORITHM = "HS256"

TOKEN_EXPIRE_HOURS = 24


# =====================================================
# PASSWORD RESET SETTINGS
# =====================================================

RESET_TOKEN_EXPIRE_MINUTES = 15


# =====================================================
# CURRENT UTC TIME
# =====================================================

def get_current_time():

    return datetime.now(
        timezone.utc
    )


# =====================================================
# CREATE USER
# =====================================================

def create_user(name, email, password):

    email = email.lower().strip()

    name = name.strip()

    # Check existing user
    existing_user = users_collection.find_one({

        "email": email

    })

    if existing_user:

        return None

    # Hash password
    hashed_password = bcrypt.hashpw(

        password.encode("utf-8"),

        bcrypt.gensalt()

    ).decode("utf-8")

    # Current time
    created_at = get_current_time()

    # User document
    user = {

        "name": name,

        "email": email,

        "password_hash": hashed_password,

        "role": "user",

        "created_at": created_at,

        "last_login": None,

        "login_count": 0

    }

    # Save to MongoDB
    result = users_collection.insert_one(
        user
    )

    return {

        "id": str(result.inserted_id),

        "name": name,

        "email": email,

        "role": "user"

    }


# =====================================================
# AUTHENTICATE USER
# =====================================================

def authenticate_user(email, password):

    email = email.lower().strip()

    # Find user
    user = users_collection.find_one({

        "email": email

    })

    if not user:

        return None

    # Get stored password
    stored_password = user.get(
        "password_hash"
    )

    if not stored_password:

        return None

    # Check password
    try:

        password_match = bcrypt.checkpw(

            password.encode("utf-8"),

            stored_password.encode("utf-8")

        )

    except Exception:

        return None

    if not password_match:

        return None

    # Get role
    role = user.get(
        "role",
        "user"
    )

    # Login information
    current_time = get_current_time()

    old_login_count = user.get(
        "login_count",
        0
    )

    new_login_count = old_login_count + 1

    # Update login information
    users_collection.update_one(

        {
            "_id": user["_id"]
        },

        {
            "$set": {

                "last_login": current_time,

                "login_count": new_login_count,

                "role": role

            }

        }

    )

    return {

        "id": str(user["_id"]),

        "name": user.get(
            "name",
            "User"
        ),

        "email": user.get(
            "email",
            email
        ),

        "role": role

    }


# =====================================================
# CREATE JWT TOKEN
# =====================================================

def create_token(user):

    expire = (

        datetime.now(
            timezone.utc
        )

        + timedelta(
            hours=TOKEN_EXPIRE_HOURS
        )

    )

    payload = {

        "user_id": user["id"],

        "name": user["name"],

        "email": user["email"],

        "role": user.get(
            "role",
            "user"
        ),

        "exp": expire

    }

    token = jwt.encode(

        payload,

        SECRET_KEY,

        algorithm=ALGORITHM

    )

    return token


# =====================================================
# VERIFY JWT TOKEN
# =====================================================

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


# =====================================================
# CHECK OWNER
# =====================================================

def is_owner(user):

    if not user:

        return False

    return user.get(
        "role",
        "user"
    ) == "owner"


# =====================================================
# GET USER BY ID
# =====================================================

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

            "name": user.get(
                "name",
                "User"
            ),

            "email": user.get(
                "email",
                ""
            ),

            "role": user.get(
                "role",
                "user"
            ),

            "created_at": user.get(
                "created_at"
            ),

            "last_login": user.get(
                "last_login"
            ),

            "login_count": user.get(
                "login_count",
                0
            )

        }

    except Exception:

        return None


# =====================================================
# CREATE PASSWORD RESET TOKEN
# =====================================================

def create_password_reset_token(email):

    email = email.lower().strip()

    # Find user
    user = users_collection.find_one({

        "email": email

    })

    if not user:

        return None

    # Generate secure random token
    raw_token = secrets.token_urlsafe(48)

    # Hash token before storing
    token_hash = hashlib.sha256(

        raw_token.encode("utf-8")

    ).hexdigest()

    # Token expiry
    expires_at = (

        get_current_time()

        + timedelta(
            minutes=RESET_TOKEN_EXPIRE_MINUTES
        )

    )

    # Store hashed token
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

    # Return raw token
    # This will later be sent through email
    return raw_token


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_password(token, new_password):

    # Hash received token
    token_hash = hashlib.sha256(

        token.encode("utf-8")

    ).hexdigest()

    # Find user using hashed token
    user = users_collection.find_one({

        "reset_token_hash": token_hash

    })

    if not user:

        return False

    # Get expiry time
    expires_at = user.get(
        "reset_token_expires"
    )

    if not expires_at:

        return False

    # Current time
    current_time = get_current_time()

    # Check expiry
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

    # =================================================
    # HASH NEW PASSWORD
    # =================================================

    hashed_password = bcrypt.hashpw(

        new_password.encode("utf-8"),

        bcrypt.gensalt()

    ).decode("utf-8")

    # =================================================
    # UPDATE PASSWORD
    # =================================================

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