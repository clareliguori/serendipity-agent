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

- You MUST read the queue_file to track URL status and check for browser requirements
- You MUST read the events_file to track discovered events
- You MUST create files if they don't exist
- You MUST check if the current URL entry in "Pending URLs" contains "(browser required)" or "(browser_required)"
- You MUST check the "Completed URLs" section for any URLs from the same domain that include "(browser_required)" in their status
- If the current URL has "(browser required)" OR any URL from the same domain has "(browser_required)", you MUST use browser_fetch for this URL without testing fetch first

### 2. Move URL to Processing

Update queue status before processing the URL.

**Constraints:**

- You MUST move the provided URL from "Pending URLs" to "Processing URLs" section
- You MUST update the queue_file with this status change

### 3. Fetch URL Content

Retrieve content from the URL using the fetch tool.

**Constraints:**

- You MUST call fetch with the url parameter
- For JSON APIs (URLs ending in `.json` or containing `/api/`), use convert_to_markdown=False
- For HTML pages, use convert_to_markdown=True (default)
- You MUST implement 1-2 second delays between requests
- If you receive a 503 error, sleep for 2 seconds and retry once

### 4. Evaluate Fetch Results

Determine if the fetched content is sufficient or if browser_fetch is needed.

**Constraints:**

- If fetch returned event information (dates, times, titles), proceed to step 5
- If you need raw HTML, call fetch again with convert_to_markdown=False
- Only use browser_fetch (step 4b) if fetch has NO event data AND shows JavaScript is required:
  - Content is mostly empty (< 500 chars)
  - "Please enable JavaScript" messages
  - Only loading placeholders, no actual events

### 4b. Use Browser Fetch (Only if needed)

**Constraints:**

- Only execute if step 4 determined browser_fetch is needed
- Call browser_fetch with url, wait_seconds=15, raw=False to get markdown-converted content

### 5. Extract Event Information

Parse content for event details, dates, and discover additional URLs.

**Constraints:**

- You MUST extract events ONLY from the current URL's content that you already fetched in step 3
- You MUST NOT call fetch or browser_fetch again in this step
- You MUST NOT "click on links" or "get more details" by fetching additional pages
- You MUST work with only the content you already have from step 3
- You MUST look for specific event instances with actual dates in the existing content
- You MUST filter events to the specified start_date to end_date timeframe
- If the content contains events for many different locations (such as tour schedules or multi-city event listings), you MUST filter to include ONLY events in the local_area parameter because users are only interested in events they can attend locally
- You MUST extract title, date, time, location, organizer, description when available from the existing content
- You MAY identify pagination links (containing "Next page", "Page 2", "More events", etc.) for adding to queue in step 7
- You MAY identify event detail page links for adding to queue in step 7
- You MUST check all discovered URLs against the entire queue_file (Pending, Processing, and Completed sections) to avoid duplicates
- If event details are incomplete in the current content, you SHOULD note what information is missing but MUST NOT fetch more pages

### 6. Filter and Score Events

Apply interest matching and relevance scoring.

**Constraints:**

- You MUST first check if the interests contain any exclusion rules (e.g., "DO NOT include events related to:", "NOT", "Reject all") and apply those exclusions BEFORE scoring
- Events matching an exclusion rule MUST be rejected regardless of how well they match a positive interest
- You MUST compare remaining events against provided positive interests
- You MUST match events to specific interests, not just individual keywords from those interests. For example, "Pressing flowers and plants" means the craft of pressing flowers/plants — not all plant-related or gardening events
- You MUST assign relevance scores
- You MUST only include moderate to high relevance events

### 7. Update Files

Write discovered events, add new URLs to queue, and update completion status.

**Constraints:**

- You MUST append new events to the existing events_file content ONLY if events were found
- You MUST NOT modify the events_file if no events were discovered
- You MUST add any discovered pagination or event detail URLs to the "Pending URLs" section of the queue_file WITHOUT fetching them
- You MUST NOT fetch discovered URLs - only add them to the queue for future processing
- You MUST move the processed URL from "Processing URLs" to "Completed URLs"
- You MUST include error information with the URL if fetch errors occurred (format: `- [x] URL_HERE (error: error_description)`)
- If you used browser_fetch because JavaScript was required, you MUST mark it as (format: `- [x] URL_HERE (status: completed, browser_required)`)
- Otherwise you MUST include success status (format: `- [x] URL_HERE (status: completed)`)
- You MUST use filesystem tools to edit files
- You MUST return only a simple summary count, not full event details
