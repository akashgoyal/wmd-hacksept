from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .models import RepoRequest, TokensModel
from .utils import call_mcp_gateway
import os
from typing import Optional

app = FastAPI(title="MCP Client API")

# Allow React frontend origin (example). In production set specific origins.
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_GATEWAY_URL = os.getenv("MCP_GATEWAY_URL", "http://docker-mcp-gateway:8000")
MCP_NAME = os.getenv("REPO_MCP_NAME", "repo-mcp")  # the registered name at docker-mcp-gateway


@app.get("/")
async def root():
    return {"message": "Hello World - MCP client server running"}


def extract_tokens_from_request(request: Request) -> dict:
    """
    Extract tokens from JSON body 'tokens' or from headers (prefixed with X-Token-)
    e.g. X-Token-GitHub, X-Token-Gemini, X-Token-Slack, X-Token-GDocs, X-Token-Cerebras
    """
    tokens = {}
    try:
        body = request.json if hasattr(request, "json") else None
    except Exception:
        body = None
    # We'll rely on endpoint handlers to parse body; here only headers:
    for k in ["Github", "Gemini", "Slack", "GDocs", "Cerebras"]:
        h = request.headers.get(f"x-token-{k.lower()}")
        if h:
            tokens[k.lower()] = h
    return tokens


async def get_tokens(payload: dict, request: Request):
    """
    Extract tokens from payload (sent by frontend) or headers.
    """
    tokens = payload.get("tokens", {})
    if not tokens:
        tokens = {
            "github": request.headers.get("X-GITHUB-TOKEN"),
            "slack": request.headers.get("X-SLACK-TOKEN"),
            "gdocs": request.headers.get("X-GDOCS-TOKEN"),
            "gemini": request.headers.get("X-GEMINI-TOKEN"),
            "cerebras": request.headers.get("X-CEREBRAS-TOKEN"),
        }
    return tokens

    
@app.post("/repo-overview")
async def repo_overview(request: Request):
    """
    Forwards to repo-mcp action: 'overview'
    """
    body = await request.json()
    tokens = await get_tokens(body, request)
    ret = await call_mcp_gateway(MCP_NAME, "overview", body, tokens)
    return ret


@app.post("/repo-commits")
async def repo_commits(request: Request):
    body = await request.json()
    tokens = await get_tokens(body, request)
    ret = await call_mcp_gateway(MCP_NAME, "commits", body, tokens)
    return ret


@app.post("/repo-collaborators")
async def repo_collaborators(request: Request):
    body = await request.json()
    tokens = await get_tokens(body, request)
    ret = await call_mcp_gateway(MCP_NAME, "collaborators", body, tokens)
    return ret


@app.post("/repo-linkedin-project")
async def repo_linkedin_project(request: Request):
    body = await request.json()
    tokens = await get_tokens(body, request)
    ret = await call_mcp_gateway(MCP_NAME, "linkedin_project", body, tokens)
    return ret


@app.post("/repo-recommendations")
async def repo_recommendations(request: Request):
    body = await request.json()
    tokens = await get_tokens(body, request)
    ret = await call_mcp_gateway(MCP_NAME, "recommendations", body, tokens)
    return ret


@app.post("/repo-meet-and-collaborators")
async def repo_meet_and_collaborators(request: Request):
    body = await request.json()
    tokens = await get_tokens(body, request)
    ret = await call_mcp_gateway(MCP_NAME, "meet_and_collaborators", body, tokens)
    return ret
