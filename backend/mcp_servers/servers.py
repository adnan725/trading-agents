import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from agents.mcp import MCPServerStdio, create_static_tool_filter

load_dotenv(override=True)

massive_api_key = os.getenv("MASSIVE_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

PROJECT_DIR = str(Path(__file__).resolve().parent.parent)
TIMEOUT = 120

if not massive_api_key:
    raise ValueError("MASSIVE_API_KEY is missing. Add it to your .env file.")

if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY is missing. Add it to your .env file."
    )

market_params = {
    "command": "uvx",
    "args": [
        "--from", "git+https://github.com/massive-com/mcp_massive@v0.10.0",
        "--with", "mcp<2",
        "mcp_massive",
    ],
    "env": {**os.environ, "MASSIVE_API_KEY": massive_api_key.strip()},
}
    

def trader_mcp_servers() -> list[MCPServerStdio]:
    """The trader mcp."""

    params = [
        {"command": "uv", "args": ["run", "-m", "backend.accounts_server"], "cwd": PROJECT_DIR},
        market_params,
    ]

    return [MCPServerStdio(p, client_session_timeout_seconds=TIMEOUT) for p in params]

def researcher_mcp_servers() -> list[MCPServerStdio]:
    """The researcher's MCP servers: Fetch and Tavily web search.

    Tavily's server offers several tools; we restrict it to web search so the
    researcher reaches for plain search rather than its heavier crawl or deep-research tools.
    """

    fetch = MCPServerStdio(
        {
            "command": "uvx",
            "args": ["--with", "mcp<2", "mcp-server-fetch",],
            "env": {**os.environ, "PYTHONIOENCODING": "utf-8",},
        },
        client_session_timeout_seconds=TIMEOUT,
    )

    search = MCPServerStdio(
        {
            "command": "npx", 
            "args": ["-y", "tavily-mcp@latest"], 
            "env": {**os.environ, "TAVILY_API_KEY": tavily_api_key}
        },
        client_session_timeout_seconds=TIMEOUT,
        tool_filter=create_static_tool_filter(allowed_tool_names=["tavily_search"]),
    )

    return [fetch, search]