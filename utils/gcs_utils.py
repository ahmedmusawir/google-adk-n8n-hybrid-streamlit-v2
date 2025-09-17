from google.cloud import storage

# --- Configuration ---
BUCKET_NAME = "adk-agent-context-ninth-potion-455712-g9"
BASE_FOLDER = "ADK_Agent_Bundle_1"

def fetch_instructions(agent_name: str) -> str:
    """Fetches agent instructions from Google Cloud Storage."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        file_path = f"{BASE_FOLDER}/{agent_name}/{agent_name}_instructions.txt"
        
        blob = bucket.blob(file_path)
        instructions = blob.download_as_text(encoding='utf-8')
        return instructions
    except Exception as e:
        print(f"ERROR fetching instructions for '{agent_name}': {e}")
        return f"Error: Could not load instructions for {agent_name}."

def update_instructions(agent_name: str, new_content: str):
    """Updates agent instructions in Google Cloud Storage."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        file_path = f"{BASE_FOLDER}/{agent_name}/{agent_name}_instructions.txt"
        
        blob = bucket.blob(file_path)
        blob.upload_from_string(new_content, content_type='text/plain')
        print(f"Successfully updated instructions for '{agent_name}' in GCS.")
    except Exception as e:
        print(f"ERROR updating instructions for '{agent_name}': {e}")
        # Optionally, re-raise the exception to be handled by the caller
        raise