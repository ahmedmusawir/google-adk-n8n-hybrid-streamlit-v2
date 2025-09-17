import streamlit as st
from utils.gcs_utils import fetch_instructions, update_instructions
from utils.auth import gatekeeper

# This one function call secures the entire page
gatekeeper()
# --- Page Configuration ---
st.set_page_config(page_title="Mission Control", page_icon="🎛️")
st.title("🎛️ Mission Control")
st.markdown("Update agent instructions in real-time.")

# --- Agent Configuration ---
AGENT_NAMES = ["greeting_agent", "calc_agent", "jarvis_agent", "product_agent"]

# --- UI for each agent ---
for agent in AGENT_NAMES:
    st.divider() # Visual separator
    st.subheader(f"Instructions for: `{agent}`")

    # Fetch current instructions
    current_instructions = fetch_instructions(agent)

    # Display in a text area
    # A unique key is crucial for Streamlit to manage the state of each text area
    new_instructions = st.text_area(
        label="Modify instructions:",
        value=current_instructions,
        height=250,
        key=f"{agent}_textarea"
    )

    # The save button
    if st.button(f"Save for {agent}", key=f"{agent}_button"):
        try:
            update_instructions(agent, new_instructions)
            st.toast(f"✅ Success! Instructions for `{agent}` updated.", icon="✅")
        except Exception as e:
            st.error(f"Failed to update instructions for {agent}. Error: {e}")