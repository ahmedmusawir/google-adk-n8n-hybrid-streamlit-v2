# Streamlit Frontend Overview

## Core Function

The Streamlit Frontend is the primary user-facing application for the entire ADK Hybrid system. It provides a secure, interactive web interface that serves as a "Mission Control" for users to engage with the suite of backend AI agents.

Its main purpose is to offer an intuitive chat experience while handling all aspects of user authentication, session management, and communication with the backend services.

---

## Key Features

The frontend is built with several key features to provide a seamless user experience:

- **Secure User Authentication**: Implements a complete login/logout system using **Supabase** for user management and authentication.
- **Agent Selection**: A simple dropdown menu allows authenticated users to select which AI agent they wish to interact with from a centrally managed list.
- **Interactive Chat UI**: A familiar, real-time chat interface for sending prompts and viewing the conversation history.
- **Persistent Sessions**: The application remembers the last active `session_id` for each agent on a per-user basis. This state is saved to the user's Supabase profile, allowing conversations to be resumed seamlessly across different login sessions.
- **Decoupled Communication**: All communication with the AI agents is proxied through the **ADK Wrapper** service. This decouples the frontend from the backend, meaning the frontend doesn't need to know the complex details of the agent bundle's location or API.

---

## Technology Stack

- **Framework**: Python with **Streamlit** for rapid development of data-centric web applications.
- **Authentication**: **Supabase** for user authentication and storing user profile data (like last used session IDs).
- **Deployment**: Deployed as a serverless container on **Google Cloud Run**.
