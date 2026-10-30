
import os
import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import get_db
from models import ChatMessage, Conversation
from context_manager import get_recent_history

# --------------------------------------------------
# 1. Load configuration
# --------------------------------------------------

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Insurance AI Copilot")

MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "amazon.nova-lite-v1:0"
)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

bedrock = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    config=__import__("botocore.config", fromlist=["Config"]).Config(
        connect_timeout=5,
        read_timeout=60,
        retries={"max_attempts": 2}
    )
)


# --------------------------------------------------
# 2. Request schema
# --------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


# --------------------------------------------------
# 3. Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "healthy"}


# --------------------------------------------------
# 4. Chat endpoint
# --------------------------------------------------

@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    logger.info("Chat request received")

    try:
        # Step 1: Retrieve recent conversation history
        messages = get_recent_history(
            db,
            request.session_id
        )

        logger.info(
            "Retrieved %s previous messages",
            len(messages)
        )

        # Step 2: Append current user message
        messages.append({
            "role": "user",
            "content": [{"text": request.message}]
        })

        # Step 3: Call AWS Bedrock
        logger.info("Calling AWS Bedrock")

        response = bedrock.converse(
            modelId=MODEL_ID,
            system=[
                {
                    "text": (
                        "You are a helpful insurance AI assistant. "
                        "Explain insurance concepts clearly. "
                        "Use conversation history to understand "
                        "follow-up questions. "
                        "Never invent policy coverage details. "
                        "If specific policy information is missing, "
                        "explain that coverage must be verified."
                    )
                }
            ],
            messages=messages,
            inferenceConfig={
                "maxTokens": 300,
                "temperature": 0.2
            }
        )

        # Step 4: Extract assistant response
        answer = "".join(
            block.get("text", "")
            for block in response["output"]["message"]["content"]
        )

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="Bedrock returned an empty response."
            )

        logger.info("Bedrock response received")

        # Step 5: Create conversation if necessary
        conversation = db.get(
            Conversation,
            request.session_id
        )

        if conversation is None:
            db.add(
                Conversation(id=request.session_id)
            )
            db.flush()

        # Step 6: Save user question and AI response
        db.add_all([
            ChatMessage(
                conversation_id=request.session_id,
                role="user",
                content=request.message
            ),
            ChatMessage(
                conversation_id=request.session_id,
                role="assistant",
                content=answer
            )
        ])

        # Step 7: Commit database transaction
        db.commit()

        logger.info("Conversation saved to PostgreSQL")

        # Step 8: Return response
        return {
            "session_id": request.session_id,
            "answer": answer,
            "history_messages_used": len(messages) - 1,
            "usage": response.get("usage", {})
        }

    except (ClientError, BotoCoreError):
        db.rollback()
        logger.exception("AWS Bedrock request failed")

        raise HTTPException(
            status_code=502,
            detail="Unable to generate an AI response."
        )

    except SQLAlchemyError:
        db.rollback()
        logger.exception("PostgreSQL operation failed")

        raise HTTPException(
            status_code=503,
            detail="Database operation failed."
        )
