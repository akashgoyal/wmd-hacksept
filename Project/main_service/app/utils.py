import os
import httpx
from typing import Dict, Any, Optional

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://docker-mcp-gateway:8080")  # adapt if needed

async def call_mcp_gateway(mcp_name: str, action: str, payload: Dict[str, Any], tokens: Optional[Dict[str,str]] = None, timeout: int = 30):
    """
    Calls the docker-mcp-gateway to execute an action on an MCP server named `mcp_name`.
    Assumes gateway exposes POST /{mcp_name}/execute with JSON { action, payload, tokens }.
    """
    url = f"{GATEWAY_URL}/{mcp_name}/execute"
    body = {"action": action, "payload": payload, "tokens": tokens or {}}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=body, timeout=timeout)
        r.raise_for_status()
        return r.json()
