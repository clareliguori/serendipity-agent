#!/usr/bin/env python3

from strands.agent import Agent
from strands.models import BedrockModel
from strands_tools import file_write, file_read, current_time
from .sub_agent_tools import run_local_search_agent, run_url_processor_agent
from botocore.config import Config
import os
from dotenv import load_dotenv


def main(parameters_file_arg=None, results_file_arg=None):
    load_dotenv()

    parameters_file = parameters_file_arg or os.getenv("PARAMETERS_FILE", "./serendipity-parameters.md")
    output_directory = os.getenv("OUTPUT_DIRECTORY", "./results")

    # Clean up previous run files
    queue_file = os.path.join(output_directory, "url-queue.md")
    events_file = os.path.join(output_directory, "events-found.md")

    if os.path.exists(queue_file):
        os.remove(queue_file)
    if os.path.exists(events_file):
        os.remove(events_file)

    boto_client_config = Config(retries={"max_attempts": 10, "mode": "standard"})

    script_path = os.path.join(os.path.dirname(__file__), "..", "agent_scripts", "serendipity-main.script.md")
    with open(script_path, "r") as f:
        script_content = f.read()

    bedrock_model = BedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        boto_client_config=boto_client_config,
    )

    agent = Agent(
        name="SerendipityOrchestrator",
        system_prompt=script_content,
        model=bedrock_model,
        tools=[
            file_write,
            file_read,
            current_time,
            run_local_search_agent,
            run_url_processor_agent,
        ],
    )

    initial_prompt = f"""Orchestrate the serendipity event finding process using sub-agents.

Parameters:
- **parameters_file**: {parameters_file}
- **output_directory**: {output_directory}
- **results_file**: {results_file_arg or "serendipity-results-yyyy-mm-dd.md (auto-generated)"}

Please coordinate the sub-agents to find and compile interesting events."""

    result = agent(initial_prompt)
    print(result)


if __name__ == "__main__":
    main()
