import json
import os
import streamlit as st
import hashlib
from helper_functions import load_user_into_session
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import init_firebase

db = init_firebase()

def get_user(username):
    doc = db.collection("users").document(username).get()
    return doc.to_dict() if doc.exists else None

def update_user(user):
    db.collection("users").document(user["username"]).set(user)

def sign_up(username, name, password):
    if get_user(username):
        raise ValueError("Username already exists.")
    user = {
        "username": username,
        "name": name,
        "password": hash_password(password),
        "total_score": 0,
        "streak": 0,
        "answered_questions": [],
        "hints_used": 0
    }
    update_user(user)
    return user

def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def login_or_signup():
    st.title("Welcome to the Agentic Python Learning App!")
    st.markdown("## This is your personalized Python learning app. 🚀Sign Up or Log In")
    auth_mode = st.radio("Choose mode:", ["Login", "Sign Up"], horizontal=True, key="auth_mode_radio")
    st.caption("🔒 Your credentials are stored securely on Google Firebase. Passwords are hashed.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Sign Up":
        name = st.text_input("Your Name")

        if st.button("Create Account"):
            try:
                user = sign_up(username, name, password)
                st.session_state.logged_in = True
                st.session_state.user = user
                load_user_into_session(user)  # ✅ Ensure session state gets initialized
                st.success(f"Account created. Welcome, {name}!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    else:  # Login mode
        if st.button("Login"):
            user = get_user(username)
            if user and user["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user = user
                load_user_into_session(user)  # ✅ This ensures total_score, streak, etc. load into session
                st.success(f"Welcome back, {user['name']}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

def check_login():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        return True
    else:
        login_or_signup()
        return False