# AI Email Automation Backend (MVP)

This is the serverless backend for the AI Email Automation application, built with **FastAPI** and orchestrated to securely interact with the **OpenAI API**.

# AI Email Automation Backend (MVP)

This is the serverless backend for the AI Email Automation application, built with **FastAPI** and orchestrated to securely interact with the **OpenAI API**.

## Architecture
The backend is designed to be lightweight, stateless, and production-ready, making it ideal for serverless deployment (e.g., AWS Lambda, Google Cloud Functions).

- **Framework:** FastAPI (Python)
- **AI Integration:** Pluggable provider abstraction (OpenAI function calling / Claude Sonnet JSON extraction)
- **Security:** JWT token validation, rate limiting, input validation
- **Logging:** Comprehensive structured logging for debugging and audit trails
- **Deployment Target:** Serverless environment or traditional servers

## Key Features

### Security
- ✅ JWT token validation on all protected endpoints
- ✅ Input validation with Pydantic models
- ✅ Rate limiting (5 requests per minute per IP)
- ✅ User authorization checks (users can only access their own data)
- ✅ Environment variable management for secrets
 - ✅ Pluggable AI providers (`OPENAI` / `CLAUDE`) with per-request override

### API Endpoints (MVP)

| Endpoint | Method | Auth | Description | Rate Limited |
| :--- | :--- | :--- | :--- | :--- |
| `/` | GET | No | Health check | No |
| `/api/v1/user/status` | GET | Yes | User subscription and usage status | No |
| **`/api/v1/ai/suggest-action`** | **POST** | **Yes** | **Core Engine: Email analysis & action suggestion** | **Yes (5/min)** |
| `/api/v1/accounts/add` | POST | Yes | Initiate OAuth flow | No |
| `/api/v1/workflows/sync` | POST | Yes | Sync user workflows | No |
| `/api/v1/actions/log` | POST | Yes | Log completed actions | No |

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- pip package manager
- OpenAI API key (get one from https://platform.openai.com/api-keys)

### 2. Installation

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python3.11 -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and add your secrets:

```bash
cp .env.example .env
```

Edit `.env` and provide (minimum for OpenAI usage):

```env
OPENAI_API_KEY=sk-your-api-key-here
JWT_SECRET=your-secure-random-secret-min-32-chars
AI_PROVIDER=openai

# If using Claude:
# CLAUDE_API_KEY=your-claude-api-key
# CLAUDE_MODEL=claude-sonnet-4.5
```

**Generate a secure JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Run Locally

```bash
# Development server with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

**Interactive API documentation:** `http://localhost:8000/docs`

## Testing

### Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest test_main.py -v

# Run with coverage report
pytest test_main.py -v --cov=. --cov-report=html
```

### Test Coverage
- EmailContext validation
- AIActionSuggestion validation
- Helper functions (personas, prompts)
- API endpoints (suggest-action, user-status, accounts, workflows)
- Authentication and authorization
- Error handling

## Usage Examples

### 1. Get User Status (Authenticated)

```bash
curl -X GET "http://localhost:8000/api/v1/user/status?user_id=user123" \
  -H "Authorization: Bearer your_jwt_token"
```

### 2. Get AI Action Suggestion (Core Endpoint)

```bash
curl -X POST "http://localhost:8000/api/v1/ai/suggest-action" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Follow up on Q3 report",
    "body": "Can you send the final Q3 report by EOD?",
    "sender": "boss@company.com",
    "user_id": "user123",
    "workflow_rules": "If from boss, draft a polite reply"
  }'
```

**Expected Response:**
```json
{
  "action": "draft_reply",
  "confidence": 0.92,
  "send_permission": "draft_only",
  "reply_text": "Thank you for your request. I'll have the Q3 report ready shortly.",
  "suggested_workflow_id": null
}
```

### 3. Override AI Provider Per Request

You can override the default provider (set by `AI_PROVIDER` in the environment) for a single request using the header `X-AI-Provider`:

```bash
curl -X POST "http://localhost:8000/api/v1/ai/suggest-action" \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -H "X-AI-Provider: claude" \
  -d '{
    "subject": "Follow up on Q3 report",
    "body": "Can you send the final Q3 report by EOD?",
    "sender": "boss@company.com",
    "user_id": "user123",
    "workflow_rules": "If from boss, draft a polite reply"
  }'
```

Ensure `CLAUDE_API_KEY` and `anthropic` dependency are configured before using `claude`.

## Deployment

### AWS Lambda + API Gateway

1. **Package the application:**
   ```bash
   pip install -r requirements.txt -t package/
   cp main.py package/
   cd package
   zip -r ../deployment.zip .
   ```

2. **Upload to Lambda:**
   - Use AWS Console or CLI
   - Set environment variables (OPENAI_API_KEY, JWT_SECRET)
   - Configure API Gateway to trigger the function

3. **Set timeout:** Minimum 30 seconds (to accommodate OpenAI API calls)

### Google Cloud Functions

```bash
gcloud functions deploy ai-email-butler-api \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point app \
  --set-env-vars OPENAI_API_KEY=sk-xxx,JWT_SECRET=xxx \
  --memory 512MB \
  --timeout 30s
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY ai_providers.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ai-email-butler-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-xxx ai-email-butler-backend
```

## Error Handling

The API returns appropriate HTTP status codes:

| Status | Meaning | Example |
| :--- | :--- | :--- |
| 200 | Success | Suggestion generated |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Accessing another user's data |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | OpenAI API failure |

## Logging

All requests and errors are logged with timestamps and user context:

```
2025-11-15 10:30:45 - main - INFO - Processing email suggestion for user user123 from boss@company.com
2025-11-15 10:30:47 - main - INFO - Successfully generated suggestion for user user123: action=draft_reply, confidence=0.92
```

## Security Best Practices

1. **Never commit `.env` files** with real secrets
2. **Use strong JWT secrets** (minimum 32 characters)
3. **Rotate JWT secrets** periodically in production
4. **Monitor API usage** and set up alerts for unusual activity
5. **Use HTTPS** in production
6. **Implement request logging** for audit trails
7. **Validate all inputs** (already implemented via Pydantic)
8. **Set appropriate timeouts** for external API calls

## Troubleshooting

### "OPENAI_API_KEY not found"
- Ensure `.env` file exists and contains `OPENAI_API_KEY`
- Check that the key is valid at https://platform.openai.com/api-keys

### "Invalid token" errors
- Ensure JWT token is properly formatted: `Bearer <token>`
- Verify token contains "sub" claim with user ID
- Check that JWT_SECRET matches the one used to generate the token

### Rate limiting errors (429)
- Default: 5 requests per minute per IP
- Wait 1-2 minutes before retrying
- Contact support if you need higher limits

### Timeout errors
- OpenAI API calls can take 5-15 seconds
- Ensure client timeout is at least 30 seconds
- Check OpenAI service status: https://status.openai.com

## CI/CD

Automated testing and deployment via GitHub Actions:
- Unit tests run on every push
- Code analysis and security scanning
- APK/artifacts built on successful tests
- See `.github/workflows/backend.yml`

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs for error messages
4. Open an issue in the repository

---

**Last Updated:** November 15, 2025
**Version:** 1.0.0-MVP
