from pydantic import BaseModel
from typing import Optional, Dict, Any

class RepoRequest(BaseModel):
    owner: str
    repo: str
    branch: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None  # any extra fields

class TokensModel(BaseModel):
    github: Optional[str] = None
    gemini: Optional[str] = None
    slack: Optional[str] = None
    gdocs: Optional[str] = None
