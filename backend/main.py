import os
import json
import logging
from typing import Optional
import jwt

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from ai_providers import get_provider, EmailContextData
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Load environment variables from .env file
load_dotenv()

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Configuration ---
# AI Provider selection
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # default provider
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # still required if provider is openai
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")  # required if provider is claude
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL")
JWT_SECRET = os.getenv("JWT_SECRET")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

# Validate required environment variables
if AI_PROVIDER.lower() == "openai" and not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found but AI_PROVIDER=openai.")
    raise ValueError("OPENAI_API_KEY not found in environment variables.")
if AI_PROVIDER.lower() == "claude" and not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY not found but AI_PROVIDER=claude.")
    raise ValueError("CLAUDE_API_KEY not found in environment variables.")

if not JWT_SECRET:
    logger.warning("JWT_SECRET not found. Using default for development only.")
    JWT_SECRET = "dev-secret-key-change-in-production"

def select_provider(request: Request) -> str:
    # Optional per-request override via header 'X-AI-Provider'
    header_val = request.headers.get("X-AI-Provider")
    if header_val:
        return header_val.strip().lower()
    return AI_PROVIDER.lower()

# Initialize FastAPI app
app = FastAPI(
    title="AI Email Automation Backend API",
    version="1.0.0",
    description="Serverless API for managing AI-driven email workflows and OpenAI integration."
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Security
security = HTTPBearer()

# --- Authentication & Authorization ---

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token from Authorization header."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT token missing 'sub' claim")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# --- Pydantic Schemas for API Request/Response ---

class EmailContext(BaseModel):
    """Schema for the email context sent from the client."""
    subject: str = Field(..., description="The subject line of the email.", min_length=1, max_length=500)
    body: str = Field(..., description="The full body content of the email.", min_length=1, max_length=10000)
    sender: str = Field(..., description="The email address of the sender.", min_length=5)
    thread_history: Optional[str] = Field(None, description="Summary of the email thread history.", max_length=5000)
    user_id: str = Field(..., description="The ID of the user requesting the action.", min_length=1)
    workflow_rules: str = Field(..., description="User-defined rules for the workflow (e.g., auto-send, persona).", min_length=1, max_length=2000)

    @validator('subject', 'body', 'workflow_rules')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v

class AIActionSuggestion(BaseModel):
    """Schema for the structured JSON output expected from the AI."""
    action: str = Field(..., description="The suggested action: 'draft_reply', 'archive', 'flag_for_review', 'schedule_meeting'.")
    confidence: float = Field(..., description="AI confidence score (0.0 to 1.0) for the suggested action.")
    send_permission: str = Field(..., description="Permission level: 'auto_send', 'draft_only', 'needs_review'.")
    reply_text: Optional[str] = Field(None, description="The generated reply text, if action is 'draft_reply'.")
    suggested_workflow_id: Optional[str] = Field(None, description="The ID of the workflow rule that was triggered.")

# --- Mock Database and Utility Functions (for MVP simulation) ---

def get_user_persona(user_id: str) -> str:
    """Mocks fetching a user's persona configuration."""
    # In a real app, this would query the 'workflows' collection in the DB
    return (
        "You are a professional, concise, and friendly assistant. "
        "Your tone should be helpful and to the point. "
        "Always use a polite closing. "
        "Your primary goal is to save the user time."
    )

def get_system_prompt(user_id: str, workflow_rules: str) -> str:
    """Constructs the full system prompt for the AI."""
    persona = get_user_persona(user_id)
    
    system_prompt = f"""
    You are an expert AI Email Automation Agent. Your task is to analyze an incoming email and suggest the best action, including a draft reply if necessary.
    
    **User Persona:** {persona}
    
    **Workflow Rules:** The user has provided the following specific rules for this email: \"{workflow_rules}\". You must adhere to these rules.
    
    **Output Requirement:** You MUST respond with a single JSON object that strictly adheres to the provided JSON schema. DO NOT include any other text, explanation, or markdown formatting outside of the JSON object.
    """
    return system_prompt

# --- API Endpoints ---

@app.get("/api/v1/user/status")
async def get_user_status(user_id: str, current_user: str = Depends(verify_jwt_token)):
    """Mocks retrieving user subscription and usage metrics."""
    if user_id != current_user:
        logger.warning(f"User {current_user} attempted to access status for user {user_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
    logger.info(f"Retrieving status for user {user_id}")
    # In a real app, this would query the 'users' collection
    return {
        "user_id": user_id,
        "subscription_status": "pro",
        "email_count_monthly": 42,
        "limit_monthly": 1000,
        "is_active": True
    }

@app.post("/api/v1/ai/suggest-action", response_model=AIActionSuggestion)
@limiter.limit("5/minute")
async def suggest_action(context: EmailContext, request: Request, current_user: str = Depends(verify_jwt_token)):
    """
    Core endpoint. Takes email context and returns a structured AI action suggestion.
    This simulates the secure, serverless call to the OpenAI API.
    Rate limited to 5 requests per minute per IP.
    """
    try:
        logger.info(f"Processing email suggestion for user {current_user} from {context.sender}")
        
        # Prepare context for provider abstraction
        ctx = EmailContextData(
            subject=context.subject,
            body=context.body,
            sender=context.sender,
            thread_history=context.thread_history,
            user_id=current_user,
            workflow_rules=context.workflow_rules,
        )
        chosen_provider = select_provider(request)
        logger.debug(f"Selecting AI provider '{chosen_provider}' for user {current_user}")
        provider_result = get_provider(chosen_provider).suggest_action(ctx)
        action_data = provider_result.data
        result = AIActionSuggestion(**action_data)
        logger.info(
            f"AI provider '{chosen_provider}' suggestion for user {current_user}: action={result.action}, confidence={result.confidence}"
        )
        return result

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"An error occurred while processing suggestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Add other mock endpoints as defined in the design (accounts, workflows, etc.)
@app.post("/api/v1/accounts/add")
async def add_account(user_id: str, provider: str, current_user: str = Depends(verify_jwt_token)):
    """Mocks initiating the OAuth flow and storing encrypted tokens."""
    if user_id != current_user:
        logger.warning(f"User {current_user} attempted to add account for user {user_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
    logger.info(f"Initiating OAuth flow for user {user_id} with provider {provider}")
    return {"status": "success", "message": f"OAuth flow initiated for user {user_id} with provider {provider}. Tokens would be stored securely."}

@app.post("/api/v1/workflows/sync")
async def sync_workflows(user_id: str, workflows: list, current_user: str = Depends(verify_jwt_token)):
    """Mocks syncing user-defined workflows."""
    if user_id != current_user:
        logger.warning(f"User {current_user} attempted to sync workflows for user {user_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access")
    
    logger.info(f"Synced {len(workflows)} workflows for user {user_id}")
    return {"status": "success", "message": f"Synced {len(workflows)} workflows for user {user_id}."}

@app.post("/api/v1/actions/log")
async def log_action(action_log: dict, current_user: str = Depends(verify_jwt_token)):
    """Mocks logging a completed or suggested action."""
    logger.info(f"Logging action for user {current_user}: {action_log.get('suggested_action')}")
    return {"status": "success", "message": "Action logged successfully."}

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "AI Email Automation Backend is running.", "status": "healthy"}

# Exception handler for rate limit errors
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
