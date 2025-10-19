Right, the final piece of documentation. Since the Streamlit app is a user interface and doesn't expose an API for other services, an `api-info.md` isn't applicable. Instead, a `config.md` detailing how the application is configured is the most logical and useful document.

Here is the `config.md` for the Streamlit frontend.

---

### `/docs/config.md`

````markdown
# Streamlit Frontend Configuration Guide

This guide details the configuration strategy for the Streamlit Frontend application. The system uses a combination of a central JSON file, environment variables, and a secrets management system to provide a flexible and secure configuration for both local development and cloud deployment.

---

## The `config.json` File

This file is the primary source of truth for environment-specific settings and the list of available agents.

**File Location:** `/[PROJECT_ROOT]/config.json`

**Structure:**

```json
{
  "environments": {
    "local": {
      "wrapper_url": "http://localhost:8080",
      "adk_bundle_url": "http://localhost:8000"
    },
    "cloud": {
      "wrapper_url": "[https://adk-wrapper-prod-v2-....run.app](https://adk-wrapper-prod-v2-....run.app)",
      "adk_bundle_url": "[https://adk-bundle-prod-v2-....run.app](https://adk-bundle-prod-v2-....run.app)"
    }
  },
  "agents": [
    "greeting_agent",
    "jarvis_agent",
    "calc_agent",
    "product_agent",
    "ghl_mcp_agent"
  ]
}
```
````

- **`environments`**: This object contains nested objects for each possible environment.
  - **`local`**: Contains the URLs for services running on the local machine.
  - **`cloud`**: Contains the live URLs for the deployed services on Google Cloud Run.
- **`agents`**: This is a simple list of strings that populates the "Choose an agent" dropdown in the user interface.

---

## Environment Variables

Environment variables are used to control which configuration block from `config.json` the application loads at startup.

### `APP_ENV`

This is the primary variable that acts as a "switch" between environments. The `config.py` script reads this variable to decide which URL settings to use.

- **To run against the cloud environment**:
  ```bash
  APP_ENV="cloud" streamlit run ./chat.py
  ```
- **To run against the local environment**:
  ```bash
  streamlit run ./chat.py
  ```
  If `APP_ENV` is not set, the application will default to **`local`**. In the Google Cloud Run deployment, the `deploy.sh` script explicitly sets `APP_ENV=cloud`.

---

## Secrets Management

Sensitive information, such as database credentials or API keys, is handled separately from the main configuration.

### Local Development

For local development, secrets are managed using Streamlit's built-in secrets functionality.

**File Location:** `/[PROJECT_ROOT]/.streamlit/secrets.toml`

```toml
# Supabase Credentials
SUPABASE_URL = "[https://your-project-ref.supabase.co](https://your-project-ref.supabase.co)"
SUPABASE_KEY = "your-supabase-anon-key"
```

### Cloud Deployment

In the deployed Google Cloud Run environment, secrets are securely injected from **Google Secret Manager**. The `deploy.sh` script maps the secrets stored in Secret Manager to the names Streamlit expects.

**Example from `deploy.sh`:**

```bash
--set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest"
```

This ensures that no sensitive values are ever stored in the source code. The application code (`st.secrets["SUPABASE_URL"]`) works seamlessly in both environments.

```

```
