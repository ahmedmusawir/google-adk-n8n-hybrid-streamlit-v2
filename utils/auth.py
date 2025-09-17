# utils/auth.py
import streamlit as st
from supabase import Client

def gatekeeper():
    """
    Checks for a valid session and stops the app if the user is not logged in.
    """
    if 'session' not in st.session_state or st.session_state.session is None:
        st.warning("⚠️ You must be logged in to access this page.")
        st.info("Please log in through the main 'chat' page to continue.")
        st.stop() # This is the key command that halts execution

def fetch_profile(supabase: Client, user_id: str) -> dict:
    """Fetches the user's profile (agent_sessions) from Supabase."""
    try:
        response = supabase.table("adk_n8n_hybrid_profiles").select("agent_sessions").eq("id", user_id).execute()
        if response.data:
            # User has an existing profile, return their saved sessions
            return response.data[0].get("agent_sessions", {})
        # New user, no profile yet
        return {}
    except Exception as e:
        st.error(f"Error fetching profile: {e}")
        return {}
    

def save_profile(supabase: Client, user_id: str, agent_sessions: dict):
    """Saves the user's agent_sessions to their profile in Supabase."""
    try:
        supabase.table("adk_n8n_hybrid_profiles").upsert({
            "id": user_id,
            "agent_sessions": agent_sessions
        }).execute()
    except Exception as e:
        st.error(f"Error saving profile: {e}")