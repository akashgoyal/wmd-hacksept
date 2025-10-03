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

MCP_NAME = os.getenv("REPO_MCP_NAME", "repo-mcp")  # the registered name at docker-mcp-gateway


@app.get("/")
async def root():
    return {"message": "Hello World - MCP client server running"}


def extract_tokens_from_request(request: Request) -> dict:
    """
    Extract tokens from JSON body 'tokens' or from headers (prefixed with X-Token-)
    e.g. X-Token-GitHub, X-Token-Gemini, X-Token-Slack, X-Token-GDocs
    """
    tokens = {}
    try:
        body = request.json if hasattr(request, "json") else None
    except Exception:
        body = None
    # We'll rely on endpoint handlers to parse body; here only headers:
    for k in ["Github", "Gemini", "Slack", "GDocs"]:
        h = request.headers.get(f"x-token-{k.lower()}")
        if h:
            tokens[k.lower()] = h
    return tokens


async def get_tokens(payload_tokens: Optional[dict], request):
    # Merge tokens from payload and headers (payload wins)
    tokens = payload_tokens.copy() if payload_tokens else {}
    for k in ["github","gemini","slack","gdocs"]:
        header_token = request.headers.get(f"x-token-{k}")
        if header_token and not tokens.get(k):
            tokens[k] = header_token
    return tokens


@app.post("/repo-overview")
async def repo_overview(req: RepoRequest, request: Request):
    """
    Forwards to repo-mcp action: 'overview'
    """
    payload = req.dict()
    ret = await call_mcp_gateway(MCP_NAME, "overview", payload, tokens=await get_tokens((request.json().get("tokens") if await request.body() else {}), request))
    return ret

@app.post("/repo-commits")
async def repo_commits(req: RepoRequest, request: Request):
    payload = req.dict()
    ret = await call_mcp_gateway(MCP_NAME, "commits", payload, tokens=await get_tokens((request.json().get("tokens") if await request.body() else {}), request))
    return ret

@app.post("/repo-collaborators")
async def repo_collaborators(req: RepoRequest, request: Request):
    payload = req.dict()
    ret = await call_mcp_gateway(MCP_NAME, "collaborators", payload, tokens=await get_tokens((request.json().get("tokens") if await request.body() else {}), request))
    return ret

@app.post("/repo-linkedin-project")
async def repo_linkedin_project(req: RepoRequest, request: Request):
    payload = req.dict()
    ret = await call_mcp_gateway(MCP_NAME, "linkedin_project", payload, tokens=await get_tokens((request.json().get("tokens") if await request.body() else {}), request), timeout=60)
    return ret

@app.post("/repo-recommendations")
async def repo_recommendations(req: RepoRequest, request: Request):
    payload = req.dict()
    ret = await call_mcp_gateway(MCP_NAME, "recommendations", payload, tokens=await get_tokens((request.json().get("tokens") if await request.body() else {}), request), timeout=60)
    return ret

@app.post("/repo-meet-and-collaborators")
async def repo_meet_and_collaborators(req: RepoRequest, request: Request):
    payload = req.dict()
    ret = await call_mcp_gateway(MCP_NAME, "meet_and_collab", payload, tokens=await get_tokens((request.json().get("tokens") if await request.body() else {}), request), timeout=60)
    return ret
