# AI Email Automation Backend (MVP)

This is the serverless backend for the AI Email Automation application, built with **FastAPI** and orchestrated to securely interact with the **OpenAI API**.

## Architecture
The backend is designed to be lightweight and stateless, making it ideal for serverless deployment (e.g., Cloudflare Workers, AWS Lambda, Google Cloud Functions).

- **Framework:** FastAPI (Python)
- **AI Integration:** OpenAI SDK (using structured JSON output via function calling)
- **Deployment Target:** Serverless environment (e.g., Vercel, Firebase Functions)

## API Endpoints (MVP)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | GET | Health check. Returns `{"message": "AI Email Automation Backend is running."}` |
| `/api/v1/user/status` | GET | Mock endpoint for user subscription and usage status. |
| **`/api/v1/ai/suggest-action`** | **POST** | **Core Workflow Engine.** Takes email context and returns a structured AI action suggestion (reply, archive, flag). |
| `/api/v1/accounts/add` | POST | Mock endpoint for initiating OAuth flow. |
| `/api/v1/workflows/sync` | POST | Mock endpoint for syncing user-defined workflows. |
| `/api/v1/actions/log` | POST | Mock endpoint for logging actions. |

## Deployment Instructions (Conceptual)

Since this is a Python-based FastAPI application, the recommended serverless deployment path is to use a platform that supports Python runtimes, such as **AWS Lambda** or **Google Cloud Functions**.

### 1. Environment Setup
1.  **Install Dependencies:**
    \`\`\`bash
    cd backend
    python3.11 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    \`\`\`
2.  **Create `requirements.txt`:**
    \`\`\`bash
    pip freeze > requirements.txt
    \`\`\`

### 2. Configure Secrets
Set the following environment variables in your chosen serverless environment:

- \`OPENAI_API_KEY\`: Your secret OpenAI API key.
- \`OPENAI_API_BASE\` (Optional): Custom base URL for the OpenAI API.

### 3. Deploy
Follow the specific deployment guide for your chosen platform (e.g., using the AWS CLI for Lambda or the Firebase CLI for Cloud Functions). The entry point for the application is the `app` object in `main.py`.

**Example for AWS Lambda (using Zappa or Serverless Framework):**
The deployment process would involve packaging the code and dependencies into a ZIP file and uploading it to Lambda, configuring an API Gateway to expose the endpoints.

**Example for Google Cloud Functions:**
The deployment command would look similar to:
\`\`\`bash
gcloud functions deploy ai-email-butler-api \
  --runtime python311 \
  --trigger-http \
  --entry-point app \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=...
\`\`\`

## Local Testing
To run the server locally for testing:
\`\`\`bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
\`\`\`
