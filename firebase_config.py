# firebase_config.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    if not firebase_admin._apps:
        # Initialize Firebase with your credentials
        firebase_config = st.secrets["firebase"]
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    return firestore.client()

