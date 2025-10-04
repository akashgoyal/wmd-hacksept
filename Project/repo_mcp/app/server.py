"""
Notes:

The MCP server uses GitHub REST API endpoints and expects a github token with proper scopes (repo/read or public access).

call_gemini is a generic stub — put your real Gemini API integration there (or use an official client).
"""

from flask import Flask, request, jsonify
from .utils import github_get, call_gemini, call_cerebras
import traceback

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "name": "repo-mcp"})

@app.route("/execute", methods=["POST"])
def execute():
    """
    Expected JSON:
    { "action": "<action>", "payload": {...}, "tokens": {"github": "...", "gemini": "...", ...} }
    """
    data = request.get_json(force=True)
    action = data.get("action")
    payload = data.get("payload") or {}
    tokens = data.get("tokens") or {}
    try:
        if action == "overview":
            return jsonify(handle_overview(payload, tokens))
        if action == "commits":
            return jsonify(handle_commits(payload, tokens))
        if action == "collaborators":
            return jsonify(handle_collaborators(payload, tokens))
        if action == "linkedin_project":
            return jsonify(handle_linkedin_project(payload, tokens))
        if action == "recommendations":
            return jsonify(handle_recommendations(payload, tokens))
        if action == "meet_and_collab":
            return jsonify(handle_meet_and_collab(payload, tokens))
        return jsonify({"error": f"unknown action {action}"}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Handlers:

def handle_overview(payload, tokens):
    owner = payload.get("owner")
    repo = payload.get("repo")
    if not owner or not repo:
        return {"error": "owner and repo required"}
    token = tokens.get("github")
    repo_data = github_get(f"https://api.github.com/repos/{owner}/{repo}", token=token)
    # return curated fields
    return {
        "name": repo_data.get("name"),
        "full_name": repo_data.get("full_name"),
        "description": repo_data.get("description"),
        "stars": repo_data.get("stargazers_count"),
        "forks": repo_data.get("forks_count"),
        "open_issues": repo_data.get("open_issues_count"),
        "language": repo_data.get("language"),
        "html_url": repo_data.get("html_url"),
        "raw": repo_data
    }

def handle_commits(payload, tokens):
    owner = payload.get("owner")
    repo = payload.get("repo")
    token = tokens.get("github")
    params = {"per_page": 100}
    commits = github_get(f"https://api.github.com/repos/{owner}/{repo}/commits", token=token, params=params)
    # return simple stats and a small list
    return {
        "commit_count_sample": len(commits),
        "latest_commits": [{"sha": c.get("sha"), "author": c.get("commit", {}).get("author", {}).get("name"), "message": c.get("commit", {}).get("message")} for c in commits[:20]],
        "raw": commits
    }

def handle_collaborators(payload, tokens):
    owner = payload.get("owner")
    repo = payload.get("repo")
    token = tokens.get("github")
    # collaborators endpoint requires appropriate permission; fallback to contributors
    try:
        collabs = github_get(f"https://api.github.com/repos/{owner}/{repo}/collaborators", token=token, params={"per_page": 100})
    except Exception:
        collabs = github_get(f"https://api.github.com/repos/{owner}/{repo}/contributors", token=token, params={"per_page": 100})
    simplified = [{"login": c.get("login"), "contributions": c.get("contributions") or None, "html_url": c.get("html_url")} for c in collabs]
    return {"collaborators": simplified, "raw": collabs}

def handle_linkedin_project(payload, tokens):
    """
    Create LinkedIn-friendly project blurb using Gemini (LLM)
    """
    owner = payload.get("owner")
    repo = payload.get("repo")
    token = tokens.get("github")
    # gemini_token = tokens.get("gemini")
    cerebras_token = tokens.get("cerebras")
    repo_data = github_get(f"https://api.github.com/repos/{owner}/{repo}", token=token)
    readme = ""
    # try to fetch README
    try:
        readme_resp = github_get(f"https://api.github.com/repos/{owner}/{repo}/readme", token=token)
        import base64, json
        content_b64 = readme_resp.get("content", "")
        if content_b64:
            readme = base64.b64decode(content_b64).decode("utf-8", errors="ignore")
    except Exception:
        readme = ""
    prompt = f"""
Write a concise LinkedIn 'Project' description (title, 1-line summary, 3 bullet points for accomplishments/tech used, and suggested hashtags) for the repository {owner}/{repo}.
Repository description: {repo_data.get('description')}
README excerpt:
{(readme[:1600] + '...') if readme else 'N/A'}
"""
    # llm_resp = call_gemini(prompt, gemini_token, max_tokens=300)
    llm_resp = call_cerebras(prompt, cerebras_token, max_tokens=300)
    # The structure depends on Gemini; return raw and text if available
    return {"linkedin_text": llm_resp.get("text") if isinstance(llm_resp, dict) else str(llm_resp), "raw": llm_resp}

def handle_recommendations(payload, tokens):
    """
    Use LLM to produce recommendations for improvements / contributors / related projects.
    """
    owner = payload.get("owner")
    repo = payload.get("repo")
    token = tokens.get("github")
    # gemini_token = tokens.get("gemini")
    cerebras_token = tokens.get("cerebras")
    # fetch basic repo info and a small set of files/commits
    repo_data = github_get(f"https://api.github.com/repos/{owner}/{repo}", token=token)
    commits = github_get(f"https://api.github.com/repos/{owner}/{repo}/commits", token=token, params={"per_page": 10})
    prompt = f"""
You are an engineering reviewer. Given repository summary:
name: {repo_data.get('full_name')}
description: {repo_data.get('description')}
recent commits (titles): {', '.join([c.get('commit', {}).get('message', '').splitlines()[0] for c in commits[:5]])}
Provide:
1) Top 5 actionable improvements (code, docs, tests, CI)
2) Suggested roles/skills of contributors who could help (3 items)
3) 3 related open-source projects to study for inspiration
Return JSON list-like text.
"""
    # resp = call_gemini(prompt, gemini_token, max_tokens=600)
    resp = call_cerebras(prompt, cerebras_token, max_tokens=600)
    return {"recommendations_raw": resp}

def handle_meet_and_collab(payload, tokens):
    """
    Create a meeting agenda and suggested collaborators to invite (based on contributors)
    """
    owner = payload.get("owner")
    repo = payload.get("repo")
    token = tokens.get("github")
    # gemini_token = tokens.get("gemini")
    cerebras_token = tokens.get("cerebras")
    contributors = github_get(f"https://api.github.com/repos/{owner}/{repo}/contributors", token=token, params={"per_page": 10})
    contrib_list = [c.get("login") for c in contributors[:6]]
    prompt = f"""
Create a 30-minute meeting agenda for discussing improvements to {owner}/{repo}. Include:
- 5 agenda items with timings
- Suggested collaborators from the list: {contrib_list} and their likely roles
- Pre-meeting reading/tasks
Return in plain text.
"""
    # resp = call_gemini(prompt, gemini_token, max_tokens=400)
    resp = call_cerebras(prompt, cerebras_token, max_tokens=400)
    return {"agenda": resp.get("text") if isinstance(resp, dict) else str(resp), "suggested_collaborators": contrib_list}
