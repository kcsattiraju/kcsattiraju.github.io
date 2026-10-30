
import json
import os
from pathlib import Path
from functools import lru_cache

import boto3
import chromadb


# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Insurance policy PDF directory
DOCUMENTS_DIR = BASE_DIR / "documents"

# Persistent Chroma vector database directory
CHROMA_DIR = BASE_DIR / "chroma_db"

# AWS Bedrock configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"

COLLECTION_NAME = "insurance_policies"


@lru_cache(maxsize=1)
def get_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=AWS_REGION
    )


@lru_cache(maxsize=1)
def get_chroma_client():
    return chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


def get_collection():
    return get_chroma_client().get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def generate_embedding(text: str) -> list[float]:
    """Generate embeddings using Amazon Titan V2."""

    client = get_bedrock_client()

    response = client.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "inputText": text,
            "dimensions": 1024,
            "normalize": True
        })
    )

    response_body = json.loads(
        response["body"].read()
    )

    return response_body["embedding"]
