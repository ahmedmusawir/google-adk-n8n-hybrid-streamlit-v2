# chat.py

import streamlit as st
import requests
import uuid
import json
from supabase import create_client, Client
from utils.auth import fetch_profile, save_profile


# --- Supabase and State Initialization ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize a session state variable to hold the user session
if 'session' not in st.session_state:
    st.session_state.session = None

# --- GATED LOGIN UI ---
# If the user is not logged in, show the login form
if st.session_state.session is None:
    st.title("⚡ Mission Control Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Authenticate")

    # The login block
    if submitted:
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email, "password": password
            })
            st.session_state.session = auth_response.session
            
            # --- ADD THIS ---
            # Fetch the user's profile and load their saved agent sessions
            user_id = st.session_state.session.user.id
            st.session_state.agent_sessions = fetch_profile(supabase, user_id)
            # --- END ADD ---

            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")

    # ================================================================
    # --- MAIN APPLICATION ---
    # ================================================================
else:
    # Get the user's permanent ID
    user_id = st.session_state.session.user.id

    # NEW: Clean state initialization
    if "agent_sessions" not in st.session_state:
        st.session_state.agent_sessions = {}
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_selected_agent" not in st.session_state:
        st.session_state.last_selected_agent = ""

    st.sidebar.write(f"Authenticated as: {st.session_state.session.user.email}")
    if st.sidebar.button("Logout"):
        st.session_state.session = None
        st.rerun()



    st.title("⚡ Cyberize Agentic Automation")
    # ... your existing sidebar, main chat logic, etc.
    N8N_WEBHOOK_URL = "http://127.0.0.1:5678/webhook/f11820f4-aaf0-4bb8-b536-b9097cc67877"
    ADK_SERVER_URL = "http://127.0.0.1:8000"

    # --- Helper Functions (No Changes) ---
    def call_n8n_webhook(agent_name, message, user_id, session_id):
        """Sends a new message to an agent via the n8n orchestrator."""
        payload = {"agent_name": agent_name, "message": message, "userId": user_id, "session_id": session_id}
        try:
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=90)
            response.raise_for_status()
            outer_data = response.json()
            data_string = outer_data.get("data")
            if data_string: return json.loads(data_string)
            return {"message": "Error: 'data' key not found."}
        except Exception as e:
            st.error(f"Failed to connect to n8n: {e}")
            return {"message": f"Error: Could not reach orchestrator. Details: {e}"}

    def fetch_history(agent_name, user_id, session_id):
        """Calls the ADK server directly to get the message history for a session."""
        if not session_id:
            return []
        try:
            url = f"{ADK_SERVER_URL}/apps/{agent_name}/users/{user_id}/sessions/{session_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            session_data = response.json()
            history = []
            if "events" in session_data:
                for event in session_data["events"]:
                    if event.get("author") in ["USER", "MODEL"] and event.get("content"):
                        role = "user" if event["author"] == "USER" else "assistant"
                        content = event["content"].get("parts", [{}])[0].get("text", "")
                        if content:
                            history.append({"role": role, "content": content})
            return history
        except Exception as e:
            st.error(f"Failed to fetch history from ADK server: {e}")
            return []

    # --- Sidebar ---
    st.sidebar.title("Configuration")
    agent_options = ["greeting_agent", "calc_agent", "jarvis_agent", "product_agent"]
    selected_agent = st.sidebar.selectbox("Choose an agent:", options=agent_options)
    st.sidebar.info(f"Chatting with: **{selected_agent}**")

    # --- Main Chat Logic ---
    if st.session_state.last_selected_agent != selected_agent:
        st.session_state.last_selected_agent = selected_agent
        resumed_session_id = st.session_state.agent_sessions.get(selected_agent)
        # st.session_state.messages = fetch_history(selected_agent, st.session_state.user_id, resumed_session_id)
        # AFTER
        st.session_state.messages = fetch_history(selected_agent, user_id, resumed_session_id)
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(f"Ask {selected_agent} a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        current_session_id = st.session_state.agent_sessions.get(selected_agent)

        with st.spinner("Orchestrator is working..."):
            response_data = call_n8n_webhook(
                agent_name=selected_agent,
                message=prompt,
                # user_id=st.session_state.user_id,
                user_id=user_id,
                session_id=current_session_id
            )

        assistant_response = response_data.get("message", "Error: No message content.")
        
        if "session_id" in response_data:
            st.session_state.agent_sessions[selected_agent] = response_data["session_id"]
            # Pass the supabase client as the first argument
            save_profile(supabase, user_id, st.session_state.agent_sessions)

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        st.rerun()