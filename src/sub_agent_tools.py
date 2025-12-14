#!/usr/bin/env python3

import os
from strands.tools import tool
from strands.agent import Agent
from strands.models.anthropic import AnthropicModel
from strands_tools import sleep
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from dotenv import load_dotenv

load_dotenv()


# Shared MCP clients - initialized once
_filesystem_mcp = None
_fetch_mcp = None

def get_filesystem_mcp():
    """Get or create the shared MCP filesystem client."""
    global _filesystem_mcp
    if _filesystem_mcp is None:
        output_dir = os.path.abspath(os.getenv("OUTPUT_DIRECTORY", "./results"))
        _filesystem_mcp = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-filesystem", output_dir],
                )
            )
        )
    return _filesystem_mcp

def get_fetch_mcp():
    """Get or create the shared MCP fetch client."""
    global _fetch_mcp
    if _fetch_mcp is None:
        _fetch_mcp = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="python",
                    args=["-W", "ignore::RuntimeWarning:asyncio", "-m", "mcp_server_fetch"],
                )
            )
        )
    return _fetch_mcp


@tool
def run_local_search_agent(
    interests: str, local_area: str, queue_file: str, start_date: str, end_date: str
) -> str:
    """Run the local search sub-agent to find events and populate the URL queue."""

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "agent_scripts", "local-search.script.md"
    )
    with open(script_path, "r") as f:
        script_content = f.read()

    brave_mcp = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@brave/brave-search-mcp-server"],
                env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")},
            )
        )
    )

    filesystem_mcp = get_filesystem_mcp()

    anthropic_model = AnthropicModel(
        client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
        model_id="claude-haiku-4-5-20251001",
        max_tokens=4096,
    )

    agent = Agent(
        name="LocalSearchAgent",
        system_prompt=script_content,
        model=anthropic_model,
        tools=[filesystem_mcp, brave_mcp],
    )

    prompt = f"""Search for local events and update the queue file.

Parameters:
- **interests**: {interests}
- **local_area**: {local_area}
- **queue_file**: {queue_file}
- **start_date**: {start_date}
- **end_date**: {end_date}

Please execute the local search process and return only the count of URLs added."""

    try:
        response = agent(prompt)
        return str(response)
    except Exception as e:
        return f"Error in local search agent: {str(e)}"


@tool
def run_url_processor_agent(
    queue_file: str,
    events_file: str,
    interests: str,
    start_date: str,
    end_date: str,
) -> str:
    """Run the URL processor sub-agent to extract events from queued URLs."""

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "agent_scripts", "url-processor.script.md"
    )
    with open(script_path, "r") as f:
        script_content = f.read()

    filesystem_mcp = get_filesystem_mcp()
    fetch_mcp = get_fetch_mcp()

    anthropic_model = AnthropicModel(
        client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
        model_id="claude-haiku-4-5-20251001",
        max_tokens=4096,
    )

    agent = Agent(
        name="URLProcessorAgent",
        system_prompt=script_content,
        model=anthropic_model,
        tools=[filesystem_mcp, fetch_mcp, sleep],
    )

    prompt = f"""Process URLs from the queue and extract events.

Parameters:
- **queue_file**: {queue_file}
- **events_file**: {events_file}
- **interests**: {interests}
- **start_date**: {start_date}
- **end_date**: {end_date}

Please execute the URL processing and return only a summary count of events found."""

    try:
        response = agent(prompt)
        return str(response)
    except Exception as e:
        return f"Error in URL processor agent: {str(e)}"
