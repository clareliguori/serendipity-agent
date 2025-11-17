# URL Processing Agent

## Overview

This agent processes URLs from a queue file, extracts event content, and writes discovered events to an events file. It handles pagination and prevents infinite loops.

## Parameters

- **queue_file** (required): Path to the URL queue file
- **events_file** (required): Path to the events output file
- **interests** (required): List of interests for filtering relevance
- **start_date** (required): Start date for event filtering
- **end_date** (required): End date for event filtering

## Steps

### 1. Load Queue and Events Files

Read current state of processing files.

**Constraints:**

- You MUST read the queue_file to get pending URLs
- You MUST read the events_file to track discovered events
- You MUST create files if they don't exist

### 2. Process First Pending URL

Extract content from the first URL in the queue.

**Constraints:**

- You MUST process only the first URL from "Pending URLs" section
- You MUST move the URL to "Processing URLs" before fetching
- You MUST NOT process URLs already in "Completed URLs"
- You MUST use fetch tool to retrieve URL content
- You MUST implement 1-2 second delays between requests
- You MUST move completed URL to "Completed URLs" with status

### 3. Extract Event Information

Parse content for event details and dates.

**Constraints:**

- You MUST look for specific event instances with actual dates
- You MUST filter events to the specified start_date to end_date timeframe
- You MUST extract title, date, time, location, description when available
- You MUST detect pagination links and event detail pages
- You MUST check new URLs against queue before adding

### 4. Filter and Score Events

Apply interest matching and relevance scoring.

**Constraints:**

- You MUST compare events against provided interests
- You MUST include related interests for broader matching
- You MUST assign relevance scores
- You MUST only include moderate to high relevance events

### 5. Update Files

Write discovered events and update queue status.

**Constraints:**

- You MUST append new events to the existing events_file content
- You MUST update queue_file with completed URLs and any new discoveries while preserving existing content
- You MUST use filesystem tools to edit files
- You MUST return only a simple summary count, not full event details
