
import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from database import SessionLocal
from context_manager import (
    get_recent_history,
    save_conversation_messages
)
from insurance_agent import agent


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Insurance Agentic AI Copilot",
    version="2.0.0"
)


# Request model
class AgentRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1)


# Token usage response
class TokenUsage(BaseModel):
    inputTokens: int = 0
    outputTokens: int = 0
    totalTokens: int = 0


# API response model
class AgentResponse(BaseModel):
    session_id: str
    answer: str
    history_messages_used: int
    usage: TokenUsage


def extract_text(content):
    """Extract readable text from an LLM message."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict)
            and isinstance(block.get("text"), str)
        )

    return str(content)


def calculate_token_usage(messages):
    """Aggregate usage across agent LLM calls."""

    input_tokens = 0
    output_tokens = 0

    for message in messages:
        usage = getattr(
            message,
            "usage_metadata",
            None
        )

        if usage:
            input_tokens += usage.get(
                "input_tokens", 0
            )
            output_tokens += usage.get(
                "output_tokens", 0
            )

    return TokenUsage(
        inputTokens=input_tokens,
        outputTokens=output_tokens,
        totalTokens=input_tokens + output_tokens
    )


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post(
    "/agent/chat",
    response_model=AgentResponse
)
def agent_chat(request: AgentRequest):

    session_id = request.session_id or str(uuid4())

    if len(session_id) > 100:
        raise HTTPException(
            status_code=422,
            detail="session_id must be at most 100 characters"
        )

    db = SessionLocal()

    try:
        # 1. Retrieve sliding-window history
        history = get_recent_history(
            db,
            session_id
        )

        # 2. Convert history into agent messages
        messages = [
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in history
        ]

        history_count = len(messages)

        # 3. Append new user message
        messages.append({
            "role": "user",
            "content": request.message
        })

        # 4. Invoke LangGraph
        result = agent.invoke({
            "messages": messages
        })

        # 5. Extract final answer
        answer = extract_text(
            result["messages"][-1].content
        )

        # 6. Aggregate token usage
        usage = calculate_token_usage(
            result["messages"]
        )

        # 7. Persist conversation
        save_conversation_messages(
            db=db,
            session_id=session_id,
            user_message=request.message,
            assistant_message=answer
        )

        return AgentResponse(
            session_id=session_id,
            answer=answer,
            history_messages_used=history_count,
            usage=usage
        )

    except Exception:
        db.rollback()
        logger.exception("Agent request failed")

        raise HTTPException(
            status_code=500,
            detail="Agent request failed. Check server logs."
        )

    finally:
        db.close()
