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

### 3. Process the Provided URL

Extract content from the specified URL parameter.

**Constraints:**

- You MUST process the URL provided in the url parameter
- If the URL ends with `.json` or contains `/api/` in the path, you MUST use the fetch tool with raw=True to retrieve JSON data directly
- Otherwise, you MUST first attempt to retrieve content using the fetch tool
- You MUST examine the fetched content for indicators that JavaScript is required to load event information
- If JavaScript is needed, you MUST use the browser_fetch tool to retrieve content
- You MUST implement 1-2 second delays between requests, made either with the fetch or browser_fetch tools
- If you receive a 503 error, you MUST sleep for 2 seconds and retry exactly once
- You MUST capture and store any fetch or browser errors for inclusion in queue status

### 4. Extract Event Information

Parse content for event details and dates, and identify additional URLs to process.

**Constraints:**

- You MUST look for specific event instances with actual dates
- You MUST filter events to the specified start_date to end_date timeframe
- You MUST extract title, date, time, location, organizer, description when available
- You MUST identify pagination links (containing "Next page", "Page 2", "More events", etc.)
- You MUST identify event detail page links that may contain additional event information
- You MUST check all discovered URLs against the entire queue_file (Pending, Processing, and Completed sections) to avoid duplicates

### 5. Filter and Score Events

Apply interest matching and relevance scoring.

**Constraints:**

- You MUST compare events against provided interests
- You MUST include related interests for broader matching
- You MUST assign relevance scores
- You MUST only include moderate to high relevance events

### 6. Update Files

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
