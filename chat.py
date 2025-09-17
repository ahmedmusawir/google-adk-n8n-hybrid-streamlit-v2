# chat.py (Final Version)

import streamlit as st
import requests
from supabase import create_client, Client
from utils.auth import fetch_profile, save_profile
from config import WRAPPER_URL, ADK_BUNDLE_URL, AGENT_OPTIONS

# --- Supabase and State Initialization (No Changes) ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if 'session' not in st.session_state:
    st.session_state.session = None

# --- Gated Login UI (No Changes) ---
if st.session_state.session is None:
    st.title("⚡ Mission Control Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Authenticate")

    if submitted:
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": email, "password": password
            })
            st.session_state.session = auth_response.session
            user_id = st.session_state.session.user.id
            st.session_state.agent_sessions = fetch_profile(supabase, user_id)
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")

# ================================================================
# --- MAIN APPLICATION ---
# ================================================================
else:
    user_id = st.session_state.session.user.id

    # Clean state initialization (No Changes)
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
    
    # --- HELPER FUNCTIONS (fetch_history updated) ---

    def call_agent_wrapper(agent_name, message, user_id, session_id):
        print(f"[STREAMLIT CALL WRAPPER] AGENT: {agent_name}, USER: {user_id}, SESSION: {session_id}")

        if not WRAPPER_URL:
            st.error("Wrapper URL is not configured. Please check config.json.")
            return {"response": "Error: Frontend is not configured."}
            
        payload = {
            "agent_name": agent_name,
            "message": message,
            "user_id": user_id,
            "session_id": session_id
        }
        try:
            response = requests.post(f"{WRAPPER_URL}/run_agent", json=payload, timeout=90)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to connect to Agent Wrapper: {e}")
            return {"response": f"Error: Could not reach Agent Wrapper. Details: {e}"}

    def fetch_history(agent_name, user_id, session_id):
        print(f"[STREAMLIT FETCH HISTORY -> WRAPPER] AGENT: {agent_name}, USER: {user_id}, SESSION: {session_id}")
        
        if not session_id or not WRAPPER_URL:
            return []
        try:
            payload = {
                "agent_name": agent_name,
                "user_id": user_id,
                "session_id": session_id,
            }
            response = requests.post(f"{WRAPPER_URL}/get_history", json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("history", [])
        except Exception as e:
            st.error(f"Failed to fetch history via wrapper: {e}")
            return []

    # --- Sidebar ---
    st.sidebar.title("Configuration")
    selected_agent = st.sidebar.selectbox("Choose an agent:", options=AGENT_OPTIONS)
    st.sidebar.info(f"Chatting with: **{selected_agent}**")

    # --- Main Chat Logic ---

    # This block runs when the user selects a new agent from the dropdown.
    # It loads the conversation history for that agent.
    if st.session_state.get("last_selected_agent") != selected_agent:
        st.session_state.last_selected_agent = selected_agent
        
        # Get the session ID bookmarked for this agent in the user's profile.
        resumed_session_id = st.session_state.agent_sessions.get(selected_agent)
        
        # Fetch the conversation history from the ADK server.
        history = fetch_history(selected_agent, user_id, resumed_session_id)
        
        # If fetch_history returned empty but we had a session ID, it means the
        # session was stale (e.g., server restarted). We must purge the bad ID.
        # if not history and resumed_session_id:
        #     st.session_state.agent_sessions.pop(selected_agent, None)
        #     print(f"Info: Cleared stale session ID for {selected_agent} from state.")
            
        # Set the messages to be displayed in the UI.
        st.session_state.messages = history
        
        # Force an immediate rerun to ensure the UI updates with the new history.
        st.rerun()

    # This loop displays the current conversation history from the session state.
    # It runs on every script rerun, showing the messages loaded above.
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # This block runs when the user submits a new message via the chat input.
    if prompt := st.chat_input(f"Ask {selected_agent} a question..."):
        # Append and display the user's message immediately for a responsive feel.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get the current session ID to continue the conversation.
        current_session_id = st.session_state.agent_sessions.get(selected_agent)

        # Call the backend to get the agent's response.
        with st.spinner("Agent is thinking..."):
            response_data = call_agent_wrapper(
                agent_name=selected_agent,
                message=prompt,
                user_id=user_id,
                session_id=current_session_id
            )

        assistant_response = response_data.get("response", "Error: No response content.")
        
        # If the backend created a new session, update our state and save the bookmark.
        new_session_id = response_data.get("session_id")
        if new_session_id and new_session_id != current_session_id:
            st.session_state.agent_sessions[selected_agent] = new_session_id
            save_profile(supabase, user_id, st.session_state.agent_sessions)

        # Append the assistant's response to the message list.
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Rerun the script to display the assistant's new message in the UI.
        st.rerun()