# Serendipity Agent

AI agent that finds events, classes, workshops that you might find interesting based on your hobbies and interests.

## Features

- Scans specified websites for events, classes, and workshops
- Performs web searches using Brave API for local events
- Filters results based on your interests and related activities
- Generates curated markdown reports with event details
- Handles pagination and date filtering (next 2 months)

## Setup

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
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
python serendipity_agent.py
```

The agent will:

1. Read your parameters from the configured files
2. Scan websites for relevant events
3. Search for local events using Brave API
4. Generate a markdown report in the output directory

## Output

Results are saved as `serendipity-results-yyyy-mm-dd.md` with:

- Summary of events found by interest category
- Events organized chronologically
- Event details including title, date, location, description, and relevance

## Requirements

- Python 3.10+
- Node.js (for Brave MCP server)
- Brave Search API key
