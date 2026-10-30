# Insurance AI Copilot

A Python insurance assistant with a Streamlit chat interface, a tool-using LangGraph agent, Amazon Bedrock models, PostgreSQL conversation storage, and hybrid retrieval over local policy PDFs.

## Technical capabilities

| Area | Implementation |
| --- | --- |
| Chat UI | Streamlit chat messages, a pinned prompt composer, thinking indicator, new conversations, and a sidebar for reopening saved conversations. |
| Persistent conversations | PostgreSQL stores conversation IDs and user/assistant messages through SQLAlchemy and psycopg. Reopened chats show their complete history and can be continued. |
| Context management | The latest 10 stored messages are passed to the agent for follow-up questions; the UI can display the full conversation. Messages are ordered by timestamp and ID. |
| Agent orchestration | LangChain `create_agent` provides a LangGraph-backed tool loop using `ChatBedrockConverse`. |
| Language model | The agent uses Amazon Nova Lite (`amazon.nova-lite-v1:0`) in `us-east-1`, with temperature 0. |
| Premium estimates | A deterministic tool computes vehicle value multiplied by the supplied annual percentage. It validates positive vehicle values and rates from 0 to 100. It does not discover or quote insurer rates. |
| Coverage explanations | A local lookup tool explains collision, comprehensive, and liability coverage in general terms. |
| Policy document questions | A retrieval tool searches indexed PDFs for deductibles, exclusions, coverage limits, and policy wording, optionally filtering by exact filename. |
| PDF ingestion | pypdf extracts text page by page; recursive splitting produces chunks of 800 characters with 150-character overlap and retains filename, page, and chunk metadata. |
| Embeddings | Amazon Titan Text Embeddings V2 (`amazon.titan-embed-text-v2:0`) generates normalized vectors with 1,024 dimensions. |
| Vector storage | A local persistent Chroma collection named `insurance_policies` uses cosine distance. Clients are cached within the process. |
| Hybrid search | Semantic search and BM25 keyword search each retrieve up to 8 candidates by default. Reciprocal rank fusion combines their ranks with a constant of 60 and returns the top 4 passages. Semantic-only and BM25-only retrieval are also available programmatically. |
| Source grounding | Retrieved passages carry chunk IDs, filenames, and page numbers. The agent prompt requests source citations, acknowledgment of missing evidence, and treatment of retrieved text as data. These are model instructions, not a guarantee of answer correctness. |
| Repeatable ingestion | SHA-256 IDs derived from filename, page, and chunk position support Chroma upserts when ingesting the same document again. |
| Agent API | FastAPI exposes `GET /health` and `POST /agent/chat` with Pydantic request/response models, generated session IDs, answer text, history counts, and aggregated input/output token usage. |
| Direct-model API | A separate `main.py` service exposes `GET /health` and `POST /chat` using boto3 Bedrock Converse without the agent tools. It validates input sizes, handles database/AWS errors, and saves exchanges. |
| AgentCore entry point | `agentcore_app.py` supplies a Bedrock AgentCore runtime entry point accepting a `prompt` and returning a response. This entry point does not use the PostgreSQL chat history handler. |
| Retrieval evaluation | An evaluation script compares semantic, BM25, and hybrid search with Recall@4, Precision@4, and mean retrieval latency against a labeled JSON dataset. |
| Local infrastructure | Docker Compose runs PostgreSQL 16 with persistent storage, a health check, and host binding `127.0.0.1:5435`. |
| Failure handling | Conversation writes use commit/rollback; UI failures show a message and log details. Database pool wait, connection, statement, and lock timeouts are configured at 5 seconds each. The prompt renders before history queries. |

## Architecture

```text
Streamlit UI -> agent_api.agent_chat -> PostgreSQL recent history
                       |
                       v
              LangGraph / LangChain agent
                       |
                Bedrock Nova Lite
                       |
        +--------------+----------------+
        |              |                |
   Premium tool   Coverage lookup   Policy search
                                        |
                              Semantic + BM25 + RRF
                                        |
                              Chroma / Titan embeddings

Successful exchanges -> PostgreSQL -> conversation history sidebar
```

The UI calls the Python API handler directly; a separate Uvicorn server is optional. PDF ingestion runs separately from the chat UI.

## Local setup

Requirements: Python compatible with the pinned packages, Docker Desktop with Compose, and AWS credentials permitted to invoke the Nova Lite and Titan embedding models in the configured region. The project was exercised with Streamlit 1.66.1. AWS model invocations can incur charges.

Run commands from this project directory. PowerShell examples:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set the password and matching database URL in `.env`. Configure AWS credentials using your normal AWS profile or environment; do not commit credentials. The agent model and region are currently specified in `insurance_agent.py`. Embedding configuration is in `rag_config.py`; its region reads `AWS_REGION` from the process environment.

```powershell
docker compose up -d
.\.venv\Scripts\python.exe -c "from database import Base, engine; import models; Base.metadata.create_all(engine)"
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Open [the local chat UI](http://localhost:8501). Schema creation is an explicit setup step; starting the UI does not create tables. The timeout settings in `database.py` target PostgreSQL.

### Index policy documents

```powershell
.\.venv\Scripts\python.exe create_sample_policy.py
.\.venv\Scripts\python.exe ingest_documents.py
```

The first command creates a fictional example PDF. For your own documents, place PDFs in `documents/` before ingestion. Extracted text and embeddings are stored locally under `chroma_db/`; text is sent to Bedrock to generate embeddings. Retrieved passages are supplied to the language model during policy questions. Scanned PDFs require separate OCR, which is not implemented.

### Optional HTTP API

```powershell
.\.venv\Scripts\python.exe -m uvicorn agent_api:app --host 127.0.0.1 --port 8000
```

Open [interactive API documentation](http://localhost:8000/docs). Example request:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/agent/chat -Method Post -ContentType application/json -Body '{"session_id":"demo-session","message":"Estimate the annual premium for a $30,000 vehicle at 4%."}'
```

The response includes `session_id`, `answer`, `history_messages_used`, and `usage` (`inputTokens`, `outputTokens`, `totalTokens`). Omit `session_id` to generate a new one. Reuse it for follow-ups.

For the alternative direct-model API, run `uvicorn main:app` and send the same fields to `/chat`; `session_id` is required there. That service reads `BEDROCK_MODEL_ID` and `AWS_REGION`. `app.py` is a standalone one-question Bedrock example, not the Streamlit entry point.

### AgentCore

`agentcore_app.py` adapts the agent to `BedrockAgentCoreApp`; run it with Python to start its runtime entry point. AWS deployment requires separate account-specific runtime configuration and permissions. Local deployment metadata and account identifiers are intentionally excluded from the repository. No hosted deployment is provisioned by these source files alone.

## Evaluation and examples

```powershell
.\.venv\Scripts\python.exe test_tools.py
.\.venv\Scripts\python.exe inspect_chunks.py
.\.venv\Scripts\python.exe evaluate_retrieval.py
```

Generate and ingest the sample policy before evaluating. `evaluation_dataset.json` contains two example questions and expected chunk IDs; inspect and update those IDs when the corpus changes. Evaluation measures retrieval quality, not generated-answer correctness. Semantic/hybrid evaluation invokes Bedrock embeddings. The small sample dataset is not a production benchmark, and the repository does not provide a comprehensive automated test suite.

Try these questions:

- What is the annual premium for a vehicle worth $30,000 at a rate of 4%?
- What does comprehensive insurance cover?
- What is the collision deductible in sample_auto_policy.pdf?
- Which exclusions are listed in my policy?

## Source map

| File | Purpose |
| --- | --- |
| `streamlit_app.py` | Chat UI and saved-conversation navigation |
| `agent_api.py` | Agent handler, HTTP endpoints, and token usage |
| `insurance_agent.py` | Model, agent prompt, and tool registration |
| `insurance_tools.py` | Premium calculation and general coverage lookup |
| `context_manager.py` | History queries and transactional exchange persistence |
| `database.py`, `models.py` | Database connection and ORM schema |
| `rag_config.py` | Chroma storage and Bedrock embeddings |
| `ingest_documents.py` | Page extraction, chunking, and vector upserts |
| `rag_tools.py` | Semantic/BM25/hybrid retrieval and document search tool |
| `evaluate_retrieval.py`, `evaluation_dataset.json` | Retrieval metrics and labels |
| `inspect_chunks.py` | Inspect stored chunk IDs and metadata |
| `create_sample_policy.py` | Generate a fictional policy for demonstrations |
| `agentcore_app.py` | AgentCore runtime adapter |
| `main.py`, `app.py` | Alternative direct Bedrock examples |
| `docker-compose.yml` | Local PostgreSQL service |

## Current limitations

- This is a local prototype with no authentication, user ownership checks, or per-user isolation. The history sidebar lists all saved conversations in its configured database. Keep the UI and APIs local unless access controls are added.
- The model can make mistakes. Premium calculations use user-supplied rates, and policy explanations are informational.
- PDF upload in the UI, OCR, response streaming, conversation deletion, migrations, and automated deployment are not implemented.
- BM25 rebuilds its corpus on each search and reads matching chunks into memory; larger datasets need additional indexing and pagination work. The history list is also unpaginated.
- Re-ingestion upserts matching chunk positions but does not remove obsolete chunks after a document shrinks or is removed. Rebuild the index when replacing a corpus where this matters.
- The agent retains only 10 recent messages as model context. Its AgentCore entry point handles a single prompt independently.
- GitHub Pages can host static content but cannot run this Python app, PostgreSQL, or its AWS integration. Publishing the source to a Pages repository does not deploy a live chatbot.

Local `.env` files, AWS deployment metadata, real policy PDFs, Chroma data, logs, virtual environments, and backup copies are excluded from version control. Create your own local configuration from `.env.example`.
