# Serendipity Event Finder

## Overview

This script discovers events, classes, and workshops that match your interests by scanning specified websites and performing targeted web searches. It uses a queue-based approach to systematically retrieve and process web pages, filtering results based on your hobbies and interests within a 2-month timeframe.

## Parameters

- **websites** (required): List of website URLs to scan for events, classes, and workshops
- **interests** (required): List of your hobbies and interests for filtering relevant events
- **local_area** (required): Your local area/city for location-based event searches
- **output_directory** (required): Directory path where the results file will be saved

**Constraints for parameter acquisition:**

- You MUST ask for all required parameters upfront in a single prompt rather than one at a time
- You MUST support multiple input methods including:
  - Direct input: Text provided directly in the conversation
  - File path: Path to a local file containing the information
  - URL: Link to an internal resource
- You MUST use appropriate tools to access content based on the input method
- You MUST confirm successful acquisition of all parameters before proceeding

## Steps

### 1. Parameter Collection and Validation

Collect all required parameters from the user and validate the inputs.

**Constraints:**

- You MUST verify that all website URLs are accessible
- You MUST ensure the output directory exists or can be created
- You MUST validate that interests list contains at least one item
- You SHOULD save parameters to a temporary file for reference during execution

### 2. Current Time Retrieval

Get the current date and time to establish the 2-month filtering window.

**Constraints:**

- You MUST use the current_time tool to get the current date and time before any other operations
- You MUST calculate the end date as exactly 2 months from the current date
- You MUST use this timeframe for all subsequent event filtering operations
- You SHOULD save the current date and end date for reference throughout the process

### 3. URL Queue and Events File Initialization

Create temporary files to track web pages and discovered events.

**Constraints:**

- You MUST create a temporary file named "url-queue.md" in the output directory
- You MUST initialize the file with sections for "Pending URLs", "Processing URLs", and "Completed URLs"
- You MUST create a temporary file named "events-found.md" in the output directory for tracking discovered events
- You MUST add all provided website URLs to the "Pending URLs" section
- You MUST use the format: `- [ ] URL_HERE (source: provided_website)`
- You MUST save both files before proceeding to search operations

### 4. Local Area Web Search and Queue Population

Perform targeted web searches and add result URLs to the processing queue.

**Constraints:**

- You MUST search for specific upcoming events with dates, not general class providers or venues
- You MUST search for each explicit interest combined with the local area and terms like "events", "classes", "workshops", "upcoming", "schedule"
- You MUST also search for related interests that logically connect to the user's stated hobbies
- You MUST use Brave search tools from the MCP server for comprehensive results
- You SHOULD search with date filters for the 2-month timeframe established in step 2 when possible
- You MUST check if each Brave search result URL already exists in the queue before adding it
- You MUST add each new relevant Brave search result URL to the "Pending URLs" section in url-queue.md
- You MUST use the format: `- [ ] URL_HERE (source: brave_search, query: "SEARCH_QUERY")`
- You MUST update the url-queue.md file after each search to maintain the queue
- You MUST prioritize official event websites and established event platforms with actual event calendars

### 5. URL Processing and Content Extraction

Process each URL in the queue, extracting content and discovering additional event pages.

**Constraints:**

- You MUST process URLs from the "Pending URLs" section one at a time
- You MUST move each URL to "Processing URLs" section before fetching it
- You MUST check if the URL already exists in the "Completed URLs" section before processing to prevent infinite loops
- You MUST NOT add URLs to "Pending URLs" if they already exist in any section of the queue file
- You MUST fetch content using the http_request tool
- You MUST NOT spend more than 2 minutes total on any single URL because timeouts can stall the entire process
- If no usable content is returned after http_request attempts, You MUST mark the URL as failed and move to the next URL
- You MUST look for specific event instances with actual dates, not general class descriptions or venue information
- You MUST detect pagination indicators such as "Next", "More", page numbers, or "Load More" buttons
- When you find pagination links or individual event detail pages, You MUST check if the URL already exists in the queue before adding it
- You MUST use the format: `- [ ] NEW_URL (source: discovered_from_PARENT_URL, type: pagination/event_detail)`
- You MUST extract event details including title, date, time, location, and description when available
- You MUST filter events to only include those occurring within the 2-month timeframe established in step 2
- You MUST move completed URLs to "Completed URLs" section with status (success/failed/timeout)
- You MUST continue processing until the "Pending URLs" section is empty
- You SHOULD implement rate limiting by using the sleep tool to wait 1-2 seconds between page requests to avoid overwhelming websites

### 6. Interest Expansion and Filtering

Expand the interests list with related activities and filter events accordingly.

**Constraints:**

- You MUST generate related interests based on the provided list (e.g., if "photography" is listed, include "digital art", "photo editing", "visual storytelling")
- You MUST compare event titles and descriptions against both explicit and related interests
- You SHOULD use semantic matching to identify relevant events even when exact keywords don't match
- You MUST assign a relevance score to each event based on interest alignment
- You SHOULD include events that match related interests with clear notation of the connection
- You SHOULD only include events with moderate to high relevance scores

### 7. Results Compilation and Output

Compile all discovered events into a structured markdown file.

**Constraints:**

- You MUST create a file named "serendipity-results-yyyy-mm-dd.md" using current_time tool to get today's date
- You MUST organize events by date in chronological order
- You MUST include for each event: title, date/time, location, full description, instructor/presenter info (if available), prerequisites, registration details, pricing, source URL, event page URL (if different from source), and relevance to interests
- You SHOULD group events by type (events, classes, workshops) within each date
- You MUST save the file to the specified output directory using file_write tool
- You SHOULD include a summary at the top showing total events found and breakdown by interest category
- You MUST delete the temporary url-queue.md file after successful completion of the results file

## Examples

### Example Parameters

```
websites: ["https://example-community-center.com", "https://local-library.org/events"]
interests: ["photography", "cooking", "woodworking", "gardening"]
local_area: "Seattle, WA"
output_directory: "/home/user/events"
```

### Example URL Queue File

```markdown
# URL Processing Queue

## Pending URLs

- [ ] https://example-community-center.com (source: provided_website)
- [ ] https://local-library.org/events (source: provided_website)
- [ ] https://eventbrite.com/seattle-photography (source: brave_search, query: "photography events Seattle")

## Processing URLs

## Completed URLs

- [x] https://example-community-center.com (status: success, events_found: 3)
```

### Example Output File Structure

```markdown
# Serendipity Results - November 16, 2025

## Summary

- Total events found: 15
- Photography: 4 events
- Cooking: 3 events
- Woodworking: 2 events
- Gardening: 3 events
- Related interests: 3 events (digital art, fermentation, sustainable living)

## November 2025

### November 20, 2025

#### Classes

**Beginner Photography Workshop**

- Time: 6:00 PM - 8:00 PM
- Location: Seattle Community Center
- Instructor: Jane Smith, Professional Photographer
- Description: Learn basic camera settings, composition rules, and lighting techniques. Hands-on practice with both digital and film cameras.
- Prerequisites: None - beginners welcome
- Registration: Required by November 18th
- Price: $45 per person
- Source: https://example-community-center.com/events
- Event Page: https://example-community-center.com/events/photography-workshop
- Relevance: High match for photography interest
```

## Troubleshooting

### Website Access Issues

If a website is inaccessible or returns errors, you should log the issue in the Completed URLs section and continue with remaining websites rather than stopping the entire process.

### HTTP Request Limitations

If websites use heavy JavaScript to load content dynamically, the http_request tool may return limited content, but you should work with whatever content is available rather than skipping the site entirely.

### Queue Management Issues

If the URL queue becomes corrupted or unreadable, you should recreate it with any remaining unprocessed URLs and continue from where you left off.

### No Events Found

If no events are found for a particular interest, you should expand search terms to include related activities and broader categories before concluding the search.
