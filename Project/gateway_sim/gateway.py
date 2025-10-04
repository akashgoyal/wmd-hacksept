# very small dev gateway that forwards /{mcp_name}/execute to http://{mcp_name}:5000/execute
from flask import Flask, request, jsonify
import requests

app = Flask("gateway-sim")

@app.route("/<mcp_name>/execute", methods=["POST"])
def execute(mcp_name):
    url = f"http://{mcp_name}:5000/execute"
    r = requests.post(url, json=request.get_json(), timeout=60)
    return (r.content, r.status_code, r.headers.items())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
