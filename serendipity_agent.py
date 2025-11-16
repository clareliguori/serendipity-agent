#!/usr/bin/env python3

from strands.agent import Agent
from strands.models import BedrockModel
from strands_tools import file_write, file_read, current_time, http_request
from strands_tools.browser import LocalChromiumBrowser
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from botocore.config import Config
import os
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Configure boto3 client with retries
    boto_client_config = Config(
        retries={
            "max_attempts": 10,
            "mode": "standard",
        }
    )

    # Load the agent script
    script_path = os.path.join(
        os.path.dirname(__file__), "serendipity-finder.script.md"
    )

    with open(script_path, "r") as f:
        script_content = f.read()

    # Create Brave MCP client
    brave_mcp = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@brave/brave-search-mcp-server"],
                env={"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")},
            )
        )
    )

    # Create browser tool
    browser_tool = LocalChromiumBrowser()

    # Create and run the agent with required tools
    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        boto_client_config=boto_client_config,
    )

    agent = Agent(
        name="SerendipityFinder",
        system_prompt=script_content,
        model=bedrock_model,
        tools=[file_write, file_read, current_time, http_request, browser_tool.browser, brave_mcp],
    )

    # Get parameters from environment and file
    parameters_file = os.getenv("PARAMETERS_FILE", "./serendipity-parameters.md")
    output_directory = os.getenv("OUTPUT_DIRECTORY", "./results")

    # Start with parameters
    initial_prompt = f"""I need help finding interesting events, classes, and workshops. Here are my parameters:

- **parameters_file**: {parameters_file} (contains websites, interests, and local_area)
- **output_directory**: {output_directory}

Please read the parameters file to get the websites, interests, and local_area, then proceed with the serendipity finding process."""

    result = agent(initial_prompt)
    print(result)


if __name__ == "__main__":
    main()
