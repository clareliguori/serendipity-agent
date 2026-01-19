#!/usr/bin/env python3

from strands.agent import Agent
from strands.models.bedrock import BedrockModel
from strands.types.content import SystemContentBlock
from strands_tools import current_time, sleep
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from .sub_agent_tools import run_local_search_agent, run_url_processor_agent
import os
from dotenv import load_dotenv
import boto3


def main(parameters_file_arg=None, results_file_arg=None):
    load_dotenv()
    
    # Create boto3 session with profile and region
    boto_session = boto3.Session(
        region_name="us-west-2",
        profile_name="personal"
    )

    parameters_file = parameters_file_arg or os.getenv("PARAMETERS_FILE")
    if not parameters_file:
        raise ValueError(
            "Parameters file must be provided via command line argument or PARAMETERS_FILE environment variable"
        )

    output_directory = os.getenv("OUTPUT_DIRECTORY", "./results")

    # Get absolute paths for MCP filesystem server allowed directories
    abs_output_dir = os.path.abspath(output_directory)
    abs_params_dir = os.path.abspath(os.path.dirname(parameters_file))
    abs_results_dir = abs_output_dir
    if results_file_arg:
        abs_results_dir = os.path.abspath(os.path.dirname(results_file_arg))

    # De-duplicate allowed directories
    allowed_dirs = list(
        dict.fromkeys([abs_output_dir, abs_params_dir, abs_results_dir])
    )

    # Create MCP filesystem client with allowed directories
    filesystem_mcp = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem"] + allowed_dirs,
            )
        )
    )

    # Clean up previous run files
    queue_file = os.path.join(output_directory, "url-queue.md")
    events_file = os.path.join(output_directory, "events-found.md")

    if os.path.exists(queue_file):
        os.remove(queue_file)
    if os.path.exists(events_file):
        os.remove(events_file)

    script_path = os.path.join(
        os.path.dirname(__file__), "..", "agent_scripts", "serendipity-main.script.md"
    )
    with open(script_path, "r") as f:
        script_content = f.read()

    bedrock_model = BedrockModel(
        model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",
        boto_session=boto_session,
        temperature=0,
    )

    # Use context manager for proper MCP lifecycle management
    with filesystem_mcp:
        tools = filesystem_mcp.list_tools_sync() + [
            current_time,
            sleep,
            run_local_search_agent,
            run_url_processor_agent,
        ]

        agent = Agent(
            name="SerendipityOrchestrator",
            system_prompt=[
                SystemContentBlock(text=script_content),
                SystemContentBlock(cachePoint={"type": "default"}),
            ],
            model=bedrock_model,
            tools=tools,
        )

        initial_prompt = f"""Orchestrate the serendipity event finding process using sub-agents.

Parameters:
- **parameters_file**: {parameters_file}
- **output_directory**: {output_directory}
- **results_file**: {results_file_arg or "serendipity-results-yyyy-mm-dd.md (auto-generated)"}

Please coordinate the sub-agents to find and compile interesting events."""

        try:
            result = agent(initial_prompt)
            print(result)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return


if __name__ == "__main__":
    main()
