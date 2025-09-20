import streamlit as st
import sqlite3
import hashlib
import os

DB_PATH = "data/users.db"

# =========================
# 🗄️ DATABASE INITIALIZATION
# =========================
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# =========================
# 🔐 PASSWORD SECURITY
# =========================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# 👤 USER REGISTRATION
# =========================
def register_user(username: str, password: str) -> bool:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# =========================
# 🔑 USER LOGIN
# =========================
def login_user(username: str, password: str) -> bool:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] == hash_password(password):
        st.session_state["logged_in_user"] = username
        return True
    return False

# =========================
# 🚪 LOGOUT
# =========================
def logout_user():
    if "logged_in_user" in st.session_state:
        del st.session_state["logged_in_user"]

# =========================
# 👀 GET CURRENT USER
# =========================
def get_current_user():
    return st.session_state.get("logged_in_user", None)
