#!/usr/bin/env python3

import os
from strands.tools import tool
from strands.agent import Agent
from strands.models import BedrockModel
from strands_tools import file_write, file_read, http_request, sleep
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()


@tool
def run_local_search_agent(
    interests: str, local_area: str, queue_file: str, start_date: str, end_date: str
) -> str:
    """Run the local search sub-agent to find events and populate the URL queue."""

    script_path = os.path.join(os.path.dirname(__file__), "..", "agent_scripts", "local-search.script.md")
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

    boto_client_config = Config(retries={"max_attempts": 10, "mode": "standard"})
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        boto_client_config=boto_client_config,
    )

    agent = Agent(
        name="LocalSearchAgent",
        system_prompt=script_content,
        model=bedrock_model,
        tools=[file_write, file_read, brave_mcp],
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
    max_urls: str = "10",
) -> str:
    """Run the URL processor sub-agent to extract events from queued URLs."""

    script_path = os.path.join(os.path.dirname(__file__), "..", "agent_scripts", "url-processor.script.md")
    with open(script_path, "r") as f:
        script_content = f.read()

    boto_client_config = Config(retries={"max_attempts": 10, "mode": "standard"})
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        boto_client_config=boto_client_config,
    )

    agent = Agent(
        name="URLProcessorAgent",
        system_prompt=script_content,
        model=bedrock_model,
        tools=[file_write, file_read, http_request, sleep],
    )

    prompt = f"""Process URLs from the queue and extract events.

Parameters:
- **queue_file**: {queue_file}
- **events_file**: {events_file}
- **interests**: {interests}
- **start_date**: {start_date}
- **end_date**: {end_date}
- **max_urls**: {max_urls}

Please execute the URL processing and return only a summary count of events found."""

    try:
        response = agent(prompt)
        return str(response)
    except Exception as e:
        return f"Error in URL processor agent: {str(e)}"
