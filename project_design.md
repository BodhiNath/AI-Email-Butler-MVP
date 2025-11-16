# Project Design: AI Email Automation Application

## 1. System Architecture (Future-Proof)

The architecture follows the recommended "thin client, smart cloud" model to ensure a lightweight app, cross-platform compatibility, and fast iteration.

| Component | Technology/Platform | Role | Future-Proofing |
| :--- | :--- | :--- | :--- |
| **Client** | **Flutter** (Dart) | Cross-platform UI, local storage, OAuth, IMAP/SMTP handling, API calls to Backend. | Single codebase for Android, PC, Web. Modular design for feature expansion (Calendar, Contacts). |
| **Backend** | **Serverless Functions** (e.g., Cloudflare Workers, Firebase Functions) | API Key Management, Usage Metering, Workflow Syncing, OpenAI API Orchestration, Optional Caching. | Scalable, cost-effective, minimal maintenance. API endpoints designed for future Calendar/Contacts services. |
| **Database** | **NoSQL/Document DB** (e.g., Firestore, DynamoDB) | Stores user profiles, subscription status, workflow rules, agent personas, usage logs, and synced data (e.g., Contact lists, Calendar events). | Flexible schema to easily add new document types for Calendar and Contacts without major refactoring. |
| **AI Layer** | **OpenAI API** (GPT-5/GPT-4.1) | Email analysis, reply generation, action suggestion (structured JSON output). | Centralized intelligence allows for easy model upgrades (e.g., from GPT-4.1 to GPT-5) without app updates. |

## 2. Database Schema Design

The schema is designed to be flexible and modular, supporting the MVP (Email) and future phases (Calendar, Contacts). We will use a document-based structure for flexibility.

### A. `users` Collection

| Field | Type | Description |
| :--- | :--- | :--- |
| `user_id` | String | Primary key (e.g., from Firebase Auth or similar). |
| `email` | String | User's primary login email. |
| `subscription_status` | String | `free`, `pro`, `expired`. Used for metering/billing. |
| `usage_metrics` | Map | Stores current month's usage (e.g., `email_count: 45`, `api_tokens: 120000`). |
| `created_at` | Timestamp | Account creation date. |

### B. `accounts` Collection (Email, Calendar, Contacts)

This collection stores credentials and metadata for all connected external accounts (e.g., Gmail, Outlook).

| Field | Type | Description |
| :--- | :--- | :--- |
| `account_id` | String | Unique ID for the connected account. |
| `user_id` | String | Foreign key to `users` collection. |
| `type` | String | `email`, `calendar`, `contacts`. **(MVP: only 'email')** |
| `provider` | String | `gmail`, `outlook`, `custom_imap`. |
| `auth_data` | Map | Encrypted OAuth tokens or IMAP/SMTP credentials. |
| `is_active` | Boolean | Status of the connection. |

### C. `workflows` Collection

Stores user-defined automation rules and agent personas.

| Field | Type | Description |
| :--- | :--- | :--- |
| `workflow_id` | String | Unique ID. |
| `user_id` | String | Foreign key to `users` collection. |
| `name` | String | User-friendly name (e.g., "Sales Lead Follow-up"). |
| `target_type` | String | `email`, `calendar_event`, `contact_update`. **(MVP: only 'email')** |
| `persona_config` | Map | Agent persona settings (e.g., `tone: 'professional'`, `style: 'concise'`). |
| `rules` | Array of Maps | Logic for when to trigger (e.g., `if_sender: 'domain.com'`, `if_subject_contains: 'invoice'`). |
| `action_mode` | String | `auto_send`, `draft_only`. |

### D. `actions` Collection (Logs)

Logs every AI-suggested or executed action for user review and auditing.

| Field | Type | Description |
| :--- | :--- | :--- |
| `action_log_id` | String | Unique ID. |
| `user_id` | String | Foreign key to `users` collection. |
| `account_id` | String | Foreign key to `accounts` collection. |
| `source_type` | String | `email`, `calendar`, `contact`. **(MVP: only 'email')** |
| `source_id` | String | ID of the email/event/contact that triggered the action. |
| `suggested_action` | String | `draft_reply`, `schedule_meeting`, `tag_contact`. |
| `confidence` | Float | AI confidence score (0.0 to 1.0). |
| `status` | String | `pending_review`, `sent`, `drafted`, `rejected`. |
| `timestamp` | Timestamp | Time of the action. |

## 3. API Endpoints (MVP Focus)

The serverless backend will expose a minimal set of secure endpoints.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/user/status` | GET | Retrieves user subscription and usage metrics. |
| `/api/v1/accounts/add` | POST | Initiates the OAuth flow and stores encrypted tokens. |
| `/api/v1/workflows/sync` | POST | Syncs user-defined workflows from the app to the database. |
| **`/api/v1/ai/suggest-action`** | **POST** | **Core endpoint.** Takes email summary/context and returns structured AI action JSON. |
| `/api/v1/actions/log` | POST | Logs a completed or suggested action. |
| `/api/v1/billing/usage` | POST | Logs usage for metering (called internally by `/ai/suggest-action`). |

## 4. GPT-5 Prompt Structure (Conceptual)

The prompt will be designed to enforce structured JSON output and incorporate user-defined persona and workflow rules.

**Input to GPT:**
1.  **System Prompt:** Defines the AI's role (e.g., "You are a professional email assistant. Your output MUST be a JSON object conforming to the provided schema.").
2.  **Persona Config:** User's desired tone, style, and voice (from `workflows.persona_config`).
3.  **Workflow Rules:** Specific instructions for the current email (e.g., "If the sender is a known client, always draft a reply. If it's spam, suggest archiving.").
4.  **Email Context:** Full email body, subject, sender, and thread history.
5.  **Output Schema:** A JSON schema definition for the required output.

**Required GPT Output (Structured JSON):**
```json
{
  "action": "draft_reply" | "archive" | "flag_for_review" | "schedule_meeting",
  "confidence": 0.92,
  "send_permission": "auto_send" | "draft_only" | "needs_review",
  "reply_text": "Hey, thanks for reaching out. I'm free tomorrow afternoon...",
  "suggested_workflow_id": "workflow_id_xyz"
}
```
