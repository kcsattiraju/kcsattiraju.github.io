import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True,
)


def create_llm(
    model_name: str | None = None,
):
    selected_model = (
        model_name
        or os.getenv("DEFAULT_MODEL")
        or "openai/gpt-oss-20b"
    )

    print(f"Using Groq model: {selected_model}")

    return ChatGroq(
        model=selected_model,
        temperature=0,
    )