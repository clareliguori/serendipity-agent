#!/usr/bin/env python3

import os
from strands.tools import tool
from strands.agent import Agent
from strands.models.anthropic import AnthropicModel
from strands_tools import sleep
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from dotenv import load_dotenv
from .serendipity_browser import SerendipityBrowser

load_dotenv()


def create_filesystem_mcp():
    """Create MCP filesystem client with allowed directories."""
    # Sub-agents only need access to output directory
    output_dir = os.path.abspath(os.getenv("OUTPUT_DIRECTORY", "./results"))

    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", output_dir],
            )
        )
    )

def create_fetch_mcp():
    """Create MCP fetch client."""
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="python",
                args=["-W", "ignore::RuntimeWarning:asyncio", "-m", "mcp_server_fetch"],
            )
        )
    )


@tool
def run_local_search_agent(
    interests: str, local_area: str, queue_file: str, start_date: str, end_date: str, max_urls_from_local_search: int = 5
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

    filesystem_mcp = create_filesystem_mcp()

    anthropic_model = AnthropicModel(
        client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
        model_id="claude-haiku-4-5-20251001",
        max_tokens=4096,
        params={"temperature": 0},
    )

    # Use context managers for proper MCP lifecycle management
    with filesystem_mcp, brave_mcp:
        tools = filesystem_mcp.list_tools_sync() + brave_mcp.list_tools_sync()
        agent = Agent(
            name="LocalSearchAgent",
            system_prompt=script_content,
            model=anthropic_model,
            tools=tools,
        )

        prompt = f"""Search for local events and update the queue file.

Parameters:
- **interests**: {interests}
- **local_area**: {local_area}
- **queue_file**: {queue_file}
- **start_date**: {start_date}
- **end_date**: {end_date}
- **max_urls_from_local_search**: {max_urls_from_local_search}

Please execute the local search process and return only the count of URLs added."""

        try:
            response = agent(prompt)
            return str(response)
        except Exception as e:
            return f"Error in local search agent: {str(e)}"


@tool
def run_url_processor_agent(
    url: str,
    queue_file: str,
    events_file: str,
    interests: str,
    start_date: str,
    end_date: str,
) -> str:
    """Run the URL processor sub-agent to extract events from a specific URL."""

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "agent_scripts", "url-processor.script.md"
    )
    with open(script_path, "r") as f:
        script_content = f.read()

    filesystem_mcp = create_filesystem_mcp()
    fetch_mcp = create_fetch_mcp()

    anthropic_model = AnthropicModel(
        client_args={"api_key": os.getenv("ANTHROPIC_API_KEY")},
        model_id="claude-haiku-4-5-20251001",
        max_tokens=4096,
        params={"temperature": 0},
    )

    # Use context managers for proper MCP lifecycle management
    with filesystem_mcp, fetch_mcp:
        browser = SerendipityBrowser()
        tools = filesystem_mcp.list_tools_sync() + fetch_mcp.list_tools_sync() + [sleep, browser.browser_fetch]
        agent = Agent(
            name="URLProcessorAgent",
            system_prompt=script_content,
            model=anthropic_model,
            tools=tools,
        )

        prompt = f"""Process the provided URL and extract events.

Parameters:
- **url**: {url}
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
