import os
import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Use the environment variables for OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

# Initialize OpenAI Client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE if OPENAI_API_BASE else None
)

# Initialize FastAPI app
app = FastAPI(
    title="AI Email Automation Backend API",
    version="1.0.0",
    description="Serverless API for managing AI-driven email workflows and OpenAI integration."
)

# --- Pydantic Schemas for API Request/Response ---

class EmailContext(BaseModel):
    """Schema for the email context sent from the client."""
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The full body content of the email.")
    sender: str = Field(..., description="The email address of the sender.")
    thread_history: Optional[str] = Field(None, description="Summary of the email thread history.")
    user_id: str = Field(..., description="The ID of the user requesting the action.")
    workflow_rules: str = Field(..., description="User-defined rules for the workflow (e.g., auto-send, persona).")

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
async def get_user_status(user_id: str):
    """Mocks retrieving user subscription and usage metrics."""
    # In a real app, this would query the 'users' collection
    return {
        "user_id": user_id,
        "subscription_status": "pro",
        "email_count_monthly": 42,
        "limit_monthly": 1000,
        "is_active": True
    }

@app.post("/api/v1/ai/suggest-action", response_model=AIActionSuggestion)
async def suggest_action(context: EmailContext):
    """
    Core endpoint. Takes email context and returns a structured AI action suggestion.
    This simulates the secure, serverless call to the OpenAI API.
    """
    try:
        # 1. Construct the full prompt
        system_prompt = get_system_prompt(context.user_id, context.workflow_rules)
        
        user_message = f"""
        **Incoming Email Details:**
        - Subject: {context.subject}
        - Sender: {context.sender}
        - Body:
        ---
        {context.body}
        ---
        
        **Thread History (if available):**
        ---
        {context.thread_history or "N/A"}
        ---
        
        Analyze the email and the user's rules, then generate the structured JSON action suggestion.
        """
        
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 2. Define the tool/function call for structured output
        tool_schema: ChatCompletionToolParam = {
            "type": "function",
            "function": {
                "name": "suggest_action",
                "description": "Suggests an action and a draft reply for an incoming email based on user rules and context.",
                "parameters": AIActionSuggestion.model_json_schema()
            }
        }

        # 3. Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using a cost-effective model for this simulation
            messages=messages,
            tools=[tool_schema],
            tool_choice={"type": "function", "function": {"name": "suggest_action"}}
        )
        
        # 4. Extract the structured JSON from the response
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            raise HTTPException(status_code=500, detail="AI failed to return a structured JSON response.")
            
        function_args = tool_calls[0].function.arguments
        
        # 5. Validate and return the Pydantic model
        action_data = json.loads(function_args)
        return AIActionSuggestion(**action_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Add other mock endpoints as defined in the design (accounts, workflows, etc.)
@app.post("/api/v1/accounts/add")
async def add_account(user_id: str, provider: str):
    """Mocks initiating the OAuth flow and storing encrypted tokens."""
    return {"status": "success", "message": f"OAuth flow initiated for user {user_id} with provider {provider}. Tokens would be stored securely."}

@app.post("/api/v1/workflows/sync")
async def sync_workflows(user_id: str, workflows: list):
    """Mocks syncing user-defined workflows."""
    return {"status": "success", "message": f"Synced {len(workflows)} workflows for user {user_id}."}

@app.post("/api/v1/actions/log")
async def log_action(action_log: dict):
    """Mocks logging a completed or suggested action."""
    return {"status": "success", "message": "Action logged successfully."}

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "AI Email Automation Backend is running."}
