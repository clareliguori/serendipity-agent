# Local Area Web Search Agent

## Overview

This agent performs targeted web searches for local events and adds relevant URLs to a processing queue file. It focuses on finding specific upcoming events with dates rather than general venues.

## Parameters

- **interests** (required): List of interests to search for
- **local_area** (required): Geographic area for location-based searches
- **queue_file** (required): Path to the URL queue file to update
- **start_date** (required): Start date for event filtering
- **end_date** (required): End date for event filtering

## Steps

### 1. Read Current Queue State

Load the existing URL queue to avoid duplicates.

**Constraints:**

- You MUST read the queue_file to get existing URLs
- You MUST track all URLs in Pending, Processing, and Completed sections
- You MUST create the queue file if it doesn't exist

### 2. Generate Search Queries

Create targeted search queries for each interest.

**Constraints:**

- You MUST search for each explicit interest combined with local_area and event terms
- You MUST include related interests that logically connect to stated hobbies
- You MUST use terms like "events", "classes", "workshops", "upcoming", "schedule"
- You SHOULD prioritize official event websites and established platforms

### 3. Execute Brave Searches

Perform web searches and collect relevant URLs.

**Constraints:**

- You MUST use Brave search tools for comprehensive results
- You MUST check each result URL against existing queue entries
- You MUST only add new URLs not already in any queue section
- You MUST add URLs with format: `- [ ] URL_HERE (source: brave_search, query: "SEARCH_QUERY")`

### 4. Update Queue File

Write new URLs to the queue file.

**Constraints:**

- You MUST read the existing queue_file content first to preserve existing structure
- You MUST append new URLs to the "Pending URLs" section only
- You MUST preserve all existing queue content and structure
- You MUST save the complete updated queue file with file_write
- You MUST return a simple count of URLs added, not the full list
