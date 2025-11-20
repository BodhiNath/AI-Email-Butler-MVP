import os
import json
import logging
from typing import Protocol

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
except ImportError:  # Graceful degradation if anthropic not installed yet
    Anthropic = None  # type: ignore


class EmailContextData:
    """Lightweight structure passed into providers (mirrors Pydantic model fields)."""
    def __init__(self, subject: str, body: str, sender: str, thread_history: str | None, user_id: str, workflow_rules: str):
        self.subject = subject
        self.body = body
        self.sender = sender
        self.thread_history = thread_history
        self.user_id = user_id
        self.workflow_rules = workflow_rules


class ProviderResult:
    def __init__(self, data: dict):
        self.data = data


class AIProvider(Protocol):
    def suggest_action(self, context: EmailContextData) -> ProviderResult: ...


def build_system_prompt(persona: str, workflow_rules: str) -> str:
    return (
        "You are an expert AI Email Automation Agent. Analyze an incoming email and "
        "suggest the best action, including a draft reply if necessary.\n\n"
        f"User Persona: {persona}\n\n"
        f"Workflow Rules: {workflow_rules}\n\n"
        "Output strictly as a single JSON object matching the schema: {\n"
        "  action: string (draft_reply | archive | flag_for_review | schedule_meeting),\n"
        "  confidence: float (0-1),\n"
        "  send_permission: string (auto_send | draft_only | needs_review),\n"
        "  reply_text: string | null,\n"
        "  suggested_workflow_id: string | null\n}"
    )


def mock_persona(user_id: str) -> str:
    return (
        "You are a professional, concise, and friendly assistant. "
        "Your tone should be helpful and to the point. Always use a polite closing. "
        "Your primary goal is to save the user time."
    )


class OpenAIProvider:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        if not api_key:
            raise ValueError("OPENAI_API_KEY missing for OpenAIProvider")
        self.client = OpenAI(api_key=api_key, base_url=base_url if base_url else None)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def suggest_action(self, context: EmailContextData) -> ProviderResult:
        persona = mock_persona(context.user_id)
        system_prompt = build_system_prompt(persona, context.workflow_rules)
        user_message = (
            f"Subject: {context.subject}\nSender: {context.sender}\nBody:\n{context.body}\n\n" \
            f"Thread History:\n{context.thread_history or 'N/A'}\n"
        )

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        tool_schema: ChatCompletionToolParam = {
            "type": "function",
            "function": {
                "name": "suggest_action",
                "description": "Suggest action and draft reply for incoming email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "confidence": {"type": "number"},
                        "send_permission": {"type": "string"},
                        "reply_text": {"type": ["string", "null"]},
                        "suggested_workflow_id": {"type": ["string", "null"]},
                    },
                    "required": ["action", "confidence", "send_permission"],
                },
            },
        }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[tool_schema],
            tool_choice={"type": "function", "function": {"name": "suggest_action"}},
        )
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            raise RuntimeError("OpenAI did not return tool calls")
        arguments = tool_calls[0].function.arguments
        data = json.loads(arguments)
        return ProviderResult(data)


class ClaudeProvider:
    def __init__(self):
        if Anthropic is None:
            raise RuntimeError("anthropic package not installed. Add 'anthropic' to requirements.")
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY missing for ClaudeProvider")
        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4.5")

    def suggest_action(self, context: EmailContextData) -> ProviderResult:
        persona = mock_persona(context.user_id)
        system_prompt = build_system_prompt(persona, context.workflow_rules)
        user_content = (
            f"Subject: {context.subject}\nSender: {context.sender}\nBody:\n{context.body}\n\nThread History:\n{context.thread_history or 'N/A'}\n" \
            "Return ONLY valid JSON."
        )
        # Anthropic messages API (simplified JSON extraction approach)
        message = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        # Combine textual content parts
        text_parts = []
        for block in message.content:
            if block.type == "text":
                text_parts.append(block.text)
        raw = "\n".join(text_parts).strip()
        # Attempt to extract JSON
        json_start = raw.find("{")
        json_end = raw.rfind("}")
        if json_start == -1 or json_end == -1:
            raise RuntimeError("Claude response did not contain JSON object")
        json_str = raw[json_start:json_end + 1]
        data = json.loads(json_str)
        return ProviderResult(data)


def get_provider(name: str) -> AIProvider:
    name = name.lower().strip()
    if name == "claude":
        return ClaudeProvider()
    return OpenAIProvider()
