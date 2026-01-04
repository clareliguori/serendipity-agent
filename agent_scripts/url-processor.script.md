# URL Processing Agent

## Overview

This agent processes a single URL provided as a parameter, extracts event content, and writes discovered events to an events file.

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

- You MUST read the queue_file to track URL status
- You MUST read the events_file to track discovered events
- You MUST create files if they don't exist

### 2. Move URL to Processing

Update queue status before processing the URL.

**Constraints:**

- You MUST move the provided URL from "Pending URLs" to "Processing URLs" section
- You MUST update the queue_file with this status change

### 3. Process the Provided URL

Extract content from the specified URL parameter.

**Constraints:**

- You MUST process the URL provided in the url parameter
- You MUST use fetch tool to retrieve URL content
- You MUST implement 1-2 second delays between requests
- You MUST capture and store any fetch errors for inclusion in queue status

### 4. Extract Event Information

Parse content for event details and dates.

**Constraints:**

- You MUST look for specific event instances with actual dates
- You MUST filter events to the specified start_date to end_date timeframe
- You MUST extract title, date, time, location, description when available
- You MUST detect pagination links and event detail pages
- You MUST check new URLs against queue before adding

### 5. Filter and Score Events

Apply interest matching and relevance scoring.

**Constraints:**

- You MUST compare events against provided interests
- You MUST include related interests for broader matching
- You MUST assign relevance scores
- You MUST only include moderate to high relevance events

### 6. Update Files

Write discovered events and update queue status with error information if applicable.

**Constraints:**

- You MUST append new events to the existing events_file content
- You MUST move the URL from "Processing URLs" to "Completed URLs" 
- You MUST include error information with the URL if fetch errors occurred (format: `- [x] URL_HERE (error: error_description)`)
- You MUST include success status if no errors occurred (format: `- [x] URL_HERE (status: completed)`)
- You MUST use filesystem tools to edit files
- You MUST return only a simple summary count, not full event details
