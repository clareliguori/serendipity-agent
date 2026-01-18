# Serendipity Agent

AI agent that finds events, classes, workshops that you might find interesting based on your hobbies and interests.

## Features

- Scans specified websites for events, classes, and workshops
- Performs web searches using Brave API for local events
- Filters results based on your interests and related activities
- Handles pagination and date filtering (configurable date range)
- Generates curated markdown reports with event details
- Modular architecture prevents context overflow issues

## Architecture

The serendipity agent uses a modular sub-agent architecture to prevent context overflow:

- **Main Orchestrator** (`serendipity_agent.py`) - Coordinates the overall process
- **Local Search Sub-Agent** - Handles Brave API searches and populates URL queue
- **URL Processor Sub-Agent** - Processes a URL from the queue and extracts events to file

Sub-agents save state in markdown files to minimize context length.

- **Queue file**: a list of URLs to scan for upcoming events
- **Events file**: a list of discovered events

### Main orchestrator

This agent manages the overall workflow while delegating intensive operations to specialized agents.

The main orchestrator will generally follow these steps:

1. Initialize the agent: Extract websites, interests, and local area from the parameters file.
   Determine date range.
   Create state files.
2. Run the local search sub-agent to populate the queue with search results.
3. For each URL in the queue, run the URL processor sub-agent to populate discovered events in the events file.
4. Generate a final markdown report describing the discovered events.

### Local search sub-agent

This agent performs targeted web searches for local events and adds relevant URLs to the queue file.
It focuses on finding specific upcoming events with dates rather than general venues.

The local search agent will generally follow these steps:

1. Generate targeted search queries for each interest described in the parameters.
2. Perform web searches using Brave and collect relevant URLs.
3. Append collected URLs to the queue file, avoiding adding duplicates already found in the file.

### URL processor sub-agent

This agent processes a given URL, extracts event content, and writes discovered events to an events file.

the URL processor agent will generally follow these steps:

1. Move the URL from "Pending" to "Processing" in the queue file.
2. Fetch the contents of the URL. Extract any event details and dates from the content.
3. Determine if the found events match provided interests and date range.
4. Add relevant events to the events file.
5. Move the URL from "Processing" to "Completed" in the queue file, describing any errors experienced.

## Setup

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Parameters

Copy and edit the environment file:

```bash
cp .env.template .env
```

Edit `.env` file:

```bash
BRAVE_API_KEY=your_brave_api_key_here
PARAMETERS_FILE=./serendipity-parameters.md
OUTPUT_DIRECTORY=./results
```

**Note:** If running in Docker, WSL, or other environments that require `--no-sandbox`, uncomment this line in `.env`:
```bash
PLAYWRIGHT_CHROMIUM_ARGS=--no-sandbox
```

Copy and edit the example parameters file:

```bash
cp serendipity-parameters-example.md serendipity-parameters.md
```

Edit `serendipity-parameters.md`:

```markdown
# Serendipity Parameters

## Websites

- https://your-community-center.com/events
- https://local-library.org/calendar

## Interests

- photography
- cooking
- hiking

## Local Area

Your City, State
```

## Usage

```bash
# Use default parameters file and auto-generated results filename
python serendipity_agent.py

# Use custom parameters file
python serendipity_agent.py my-custom-parameters.md

# Use custom parameters file and custom results filename
python serendipity_agent.py my-custom-parameters.md results/my-results.md
```

## File Structure

- `serendipity_agent.py` - Main entry point
- `src/orchestrator_agent.py` - Main orchestrator implementation
- `src/sub_agent_tools.py` - Sub-agent tool wrappers
- `agent_scripts/serendipity-main.script.md` - Main orchestrator script
- `agent_scripts/local-search.script.md` - Local search sub-agent script
- `agent_scripts/url-processor.script.md` - URL processor sub-agent script

## Output

Results are saved as `serendipity-results-yyyy-mm-dd.md` with:

- Summary of events found by interest category
- Events organized chronologically
- Event details including title, date, location, description, and relevance

## Requirements

- Python 3.10+
- Node.js (for Brave MCP server)
- Brave Search API key
