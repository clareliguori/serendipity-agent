# URL Processing Agent

## Overview

The serendipity agent finds events, classes, and workshops that match user interests by scanning websites and performing web searches.

As part of this agent, you process an individual URL to extract event information.

## Parameters

- **url** (required): The specific URL to process
- **queue_file** (required): Path to the URL queue file for status tracking
- **events_file** (required): Path to the events output file
- **interests** (required): List of interests for filtering relevance
- **start_date** (required): Start date for event filtering
- **end_date** (required): End date for event filtering

## Steps

### 1. Load Queue and Events Files

Read current state of processing files.

**Constraints:**

- You MUST read the queue_file to track URL status and check for domain-level browser requirements
- You MUST read the events_file to track discovered events
- You MUST create files if they don't exist
- You MUST check the "Completed URLs" section for any URLs from the same domain that include "(browser_required)" in their status
- If any URL from the same domain has "(browser_required)", you MUST use browser_fetch for this URL without testing fetch first

### 2. Move URL to Processing

Update queue status before processing the URL.

**Constraints:**

- You MUST move the provided URL from "Pending URLs" to "Processing URLs" section
- You MUST update the queue_file with this status change

### 3. Fetch URL Content

Retrieve content from the URL using the fetch tool.

**Constraints:**

- You MUST process the URL provided in the url parameter
- If the URL ends with `.json` or contains `/api/` in the path, you MUST use the fetch tool with raw=True to retrieve JSON data directly
- Otherwise, you MUST use the fetch tool with max_length=50000
- You MUST make exactly ONE fetch call
- You MUST implement 1-2 second delays between requests
- If you receive a 503 error, you MUST sleep for 2 seconds and retry exactly once
- You MUST capture and store any fetch errors for inclusion in queue status

### 4. Evaluate Fetch Results

Determine if the fetched content is sufficient or if browser_fetch is needed.

**Constraints:**

- You MUST examine the fetched content for event information (dates, times, titles, descriptions)
- If the fetch returned ANY event information at all, you MUST proceed to step 5 (Extract Event Information)
- If you need more content or raw HTML, you MUST use fetch again with different parameters (start_index for pagination, raw=True for HTML)
- You MUST NOT use browser_fetch to get "more content" or "raw HTML" - use fetch with start_index or raw=True instead
- You MUST only proceed to step 4b (Use Browser Fetch) if ALL of these conditions are true:
  - Content is mostly empty (less than 500 characters of actual text)
  - OR page shows "Please enable JavaScript" or similar messages
  - OR content contains only loading placeholders or skeleton screens
  - AND page has NO event information at all (no dates, no titles, no event names)
- "Limited content", "partial results", or "need raw HTML" is NOT a reason to use browser_fetch

### 4b. Use Browser Fetch (Only if Step 4 determined it's needed)

Retrieve content using browser with JavaScript rendering.

**Constraints:**

- You MUST only execute this step if step 4 determined browser_fetch is needed
- You MUST use browser_fetch with wait_seconds=15, raw=True, max_length=200000
- You MUST capture and store any browser errors for inclusion in queue status

### 5. Extract Event Information

Parse content for event details and dates, and identify additional URLs to process.

**Constraints:**

- You MUST look for specific event instances with actual dates
- You MUST filter events to the specified start_date to end_date timeframe
- You MUST extract title, date, time, location, organizer, description when available
- You MUST identify pagination links (containing "Next page", "Page 2", "More events", etc.)
- You MUST identify event detail page links that may contain additional event information
- You MUST check all discovered URLs against the entire queue_file (Pending, Processing, and Completed sections) to avoid duplicates

### 6. Filter and Score Events

Apply interest matching and relevance scoring.

**Constraints:**

- You MUST compare events against provided interests
- You MUST include related interests for broader matching
- You MUST assign relevance scores
- You MUST only include moderate to high relevance events

### 7. Update Files

Write discovered events, add new URLs to queue, and update completion status.

**Constraints:**

- You MUST append new events to the existing events_file content ONLY if events were found
- You MUST NOT modify the events_file if no events were discovered
- You MUST add any discovered pagination or event detail URLs that have not yet been fetched to the "Pending URLs" section of the queue_file, so that other URL processing agents can process them
- You MUST move the processed URL from "Processing URLs" to "Completed URLs"
- You MUST include error information with the URL if fetch errors occurred (format: `- [x] URL_HERE (error: error_description)`)
- If you used browser_fetch because JavaScript was required, you MUST mark it as (format: `- [x] URL_HERE (status: completed, browser_required)`)
- Otherwise you MUST include success status (format: `- [x] URL_HERE (status: completed)`)
- You MUST use filesystem tools to edit files
- You MUST return only a simple summary count, not full event details
