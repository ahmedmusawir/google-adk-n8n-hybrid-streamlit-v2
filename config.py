# config.py
import os
import json

def load_config():
    """
    Loads configuration from config.json based on APP_ENV environment variable.
    Defaults to 'local' if APP_ENV is not set.
    """
    # 1. Determine the environment ('local' or 'cloud')
    env = os.getenv("APP_ENV", "local").lower()

    # 2. Load the entire config file
    with open('config.json', 'r') as f:
        config_data = json.load(f)

    # 3. Get the settings for the determined environment
    env_config = config_data.get("environments", {}).get(env)
    if not env_config:
        raise ValueError(f"Configuration for environment '{env}' not found in config.json")

    # 4. Return the specific URLs and agent options
    return {
        "wrapper_url": env_config.get("wrapper_url"),
        "adk_bundle_url": env_config.get("adk_bundle_url"),
        "agent_options": config_data.get("agents", [])
    }

# Load the configuration once when the module is imported
_config = load_config()

# Export variables for the app to use (e.g., from chat import WRAPPER_URL)
WRAPPER_URL = _config["wrapper_url"]
ADK_BUNDLE_URL = _config["adk_bundle_url"]
AGENT_OPTIONS = _config["agent_options"]

# Print the mode for verification when the app starts
print(f"✅ Config loaded for [ {os.getenv('APP_ENV', 'local').upper()} ] mode.")
print(f"   -> Wrapper URL: {WRAPPER_URL}")