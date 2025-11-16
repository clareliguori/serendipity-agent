# Serendipity Event Finder - Main Orchestrator

## Overview

This script orchestrates the serendipity event finding process by coordinating sub-agents that handle specific tasks. It manages the overall workflow while delegating intensive operations to specialized agents to avoid context overflow.

## Parameters

- **parameters_file** (required): Path to file containing websites, interests, and local_area
- **output_directory** (required): Directory path where result files will be saved
- **results_file** (optional): Custom filename for results (defaults to serendipity-results-yyyy-mm-dd.md)

## Steps

### 1. Parameter Collection and Setup

Read parameters and initialize the process.

**Constraints:**

- You MUST read the parameters_file to extract websites, interests, and local_area
- You MUST ensure the output_directory exists or create it
- You MUST get current time and calculate start_date as current date and end_date as 2 months from now
- You MUST create queue_file and events_file paths in output_directory

### 2. Initialize Queue File

Create the URL processing queue with provided websites.

**Constraints:**

- You MUST create "url-queue.md" in output_directory
- You MUST initialize with sections: "Pending URLs", "Processing URLs", "Completed URLs"
- You MUST add all provided website URLs to "Pending URLs" section
- You MUST use format: `- [ ] URL_HERE (source: provided_website)`

### 3. Execute Local Search Sub-Agent

Run the local search agent to populate the queue with search results.

**Constraints:**

- You MUST use run_local_search_agent tool with interests, local_area, queue_file, start_date, and end_date
- You MUST capture only the count result, not full output
- You SHOULD retry once if the sub-agent fails

### 4. Execute URL Processing Sub-Agent

Run the URL processor agent to extract events from queued URLs.

**Constraints:**

- You MUST use run_url_processor_agent tool with queue_file, events_file, interests, start_date, end_date
- You MUST process in batches of 10 URLs maximum per run
- You MUST continue calling until no pending URLs remain or reasonable limit reached
- You MUST capture only summary counts, not full event details

### 5. Compile Final Results

Read extracted events and create the final formatted report.

**Constraints:**

- You MUST read the events_file to get all discovered events
- You MUST create the results file using the provided results_file parameter if specified, otherwise use "serendipity-results-yyyy-mm-dd.md" format with current date
- You MUST organize events chronologically by date
- You MUST include summary statistics by interest category
- You MUST clean up temporary files (url-queue.md, events-found.md)
