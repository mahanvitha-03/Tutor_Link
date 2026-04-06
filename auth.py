"""
auth.py — Authentication logic: registration, login, password hashing

ENHANCEMENTS:
  - get_current_user() now returns theme preference from DB
  - set_session() saves theme to session_state
"""

import bcrypt
import streamlit as st
from database import create_user, get_user_by_username, get_user_by_id


def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def register_user(username, password, role, full_name, email, mobile_number=""):
    if not username or not password or not full_name:
        return False, "Username, password, and full name are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if " " in username:
        return False, "Username cannot contain spaces."
    if get_user_by_username(username):
        return False, f"Username '{username}' is already taken."
    password_hash = hash_password(password)
    user_id = create_user(username, password_hash, role, full_name, email, mobile_number)
    if user_id:
        return True, user_id
    return False, "Registration failed. Please try again."


def login_user(username, password):
    if not username or not password:
        return False, "Please enter both username and password."
    user = get_user_by_username(username)
    if not user:
        return False, "No account found with that username."
    if not verify_password(password, user["password"]):
        return False, "Incorrect password. Please try again."
    return True, user


def set_session(user: dict):
    """Save logged-in user data including theme to Streamlit session state."""
    st.session_state["logged_in"]  = True
    st.session_state["user_id"]    = user["id"]
    st.session_state["username"]   = user["username"]
    st.session_state["role"]       = user["role"]
    st.session_state["full_name"]  = user["full_name"]
    # Persist theme preference
    st.session_state["theme_override"] = user.get("theme", "dark")


def logout():
    """Clear all session state keys."""
    keys = ["logged_in", "user_id", "username", "role", "full_name",
            "theme_override", "page", "prev_page", "booking_tutor_id"]
    for key in keys:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def get_current_user() -> dict:
    """
    Return info about the currently logged-in user.
    Fetches fresh DB row so theme and other fields are always current.
    """
    if not is_logged_in():
        return {}
    user_id = st.session_state.get("user_id")
    db_user = get_user_by_id(user_id)
    if db_user:
        return db_user
    # Fallback to session data
    return {
        "id":        st.session_state.get("user_id"),
        "username":  st.session_state.get("username"),
        "role":      st.session_state.get("role"),
        "full_name": st.session_state.get("full_name"),
        "theme":     st.session_state.get("theme_override", "dark"),
    }
