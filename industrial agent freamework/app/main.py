from contextlib import asynccontextmanager
from app.api.chat_routes import router as chat_router
from app.api.tool_routes import router as tool_router

from fastapi import FastAPI

from app.api.agent_routes import (
    router as agent_router,
)

from app.api.tool_routes import (
    router as tool_router,
)

from app.api.chat_routes import (
    router as chat_router,
)

from app.database.setup import (
    setup_database,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    setup_database()

    yield


app = FastAPI(
    title="Agentic AI Platform",
    description=(
        "Generic platform for creating, "
        "configuring and executing AI agents."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(agent_router)
app.include_router(tool_router)
app.include_router(chat_router)


@app.get("/")
def root():

    return {
        "application": "Agentic AI Platform",
        "version": "0.1.0",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }