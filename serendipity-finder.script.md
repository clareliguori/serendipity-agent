# Serendipity Event Finder

## Overview

This script discovers events, classes, and workshops that match your interests by scanning specified websites and performing targeted web searches. It filters results based on your hobbies and interests, focusing on events occurring within the next 2 months, and outputs a curated list to a markdown file.

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

### 3. Website Content Extraction

Scan each provided website for specific upcoming events with dates, following pagination to collect all relevant events.

**Constraints:**

- You MUST first attempt to fetch content from each website URL using the http_request tool
- If http_request returns no events or minimal content, You MUST retry using the local_chromium_browser tool because the site likely uses JavaScript to load content dynamically
- You MUST look for specific event instances with actual dates, not general class descriptions or venue information
- You MUST NOT include venues, organizations, or class providers unless they have specific upcoming events with dates listed
- You MUST detect pagination indicators such as "Next", "More", page numbers, or "Load More" buttons
- You MUST follow pagination links to retrieve additional pages until no more events within the 2-month timeframe are found
- You MUST look for event indicators such as dates, times, locations, and event descriptions on each page
- You SHOULD search for common event-related keywords: "event", "class", "workshop", "seminar", "conference", "meetup"
- You MUST extract event details including title, date, time, location, and description when available
- You MUST filter events to only include those occurring within the 2-month timeframe established in step 2
- You MUST stop pagination when reaching events outside the 2-month window or when no more pages exist
- You SHOULD implement reasonable rate limiting between page requests to avoid overwhelming websites

### 4. Interest Expansion and Filtering

Expand the interests list with related activities and filter events accordingly.

**Constraints:**

- You MUST generate related interests based on the provided list (e.g., if "photography" is listed, include "digital art", "photo editing", "visual storytelling")
- You MUST compare event titles and descriptions against both explicit and related interests
- You SHOULD use semantic matching to identify relevant events even when exact keywords don't match
- You MUST assign a relevance score to each event based on interest alignment
- You SHOULD include events that match related interests with clear notation of the connection
- You SHOULD only include events with moderate to high relevance scores

### 5. Local Area Web Search

Perform targeted web searches for specific upcoming events with dates in the user's local area using both explicit and related interests.

**Constraints:**

- You MUST search for specific upcoming events with dates, not general class providers or venues
- You MUST search for each explicit interest combined with the local area and terms like "events", "classes", "workshops", "upcoming", "schedule"
- You MUST also search for related interests that logically connect to the user's stated hobbies
- You MUST use Brave search tools from the MCP server for comprehensive results
- You SHOULD search with date filters for the 2-month timeframe established in step 2 when possible
- You MUST extract specific event details from search results including dates and times
- You MUST NOT include general venue descriptions or "about us" pages without specific event dates
- You SHOULD prioritize official event websites and established event platforms with actual event calendars
- You MUST clearly indicate in results whether an event matches explicit or related interests

### 5. Results Compilation and Output

Compile all discovered events into a structured markdown file.

**Constraints:**

- You MUST create a file named "serendipity-results-yyyy-mm-dd.md" using current_time tool to get today's date
- You MUST organize events by date in chronological order
- You MUST include for each event: title, date/time, location, description, source URL, and relevance to interests
- You SHOULD group events by type (events, classes, workshops) within each date
- You MUST save the file to the specified output directory using file_write tool
- You SHOULD include a summary at the top showing total events found and breakdown by interest category

## Examples

### Example Parameters

```
websites: ["https://example-community-center.com", "https://local-library.org/events"]
interests: ["photography", "cooking", "woodworking", "gardening"]
local_area: "Seattle, WA"
output_directory: "/home/user/events"
```

### Example Output File Structure

```markdown
# Serendipity Results - November 15, 2025

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
- Description: Learn basic camera settings and composition
- Source: https://example-community-center.com
- Relevance: High match for photography interest

**Digital Art Fundamentals**

- Time: 7:00 PM - 9:00 PM
- Location: Art Studio Downtown
- Description: Introduction to digital painting and design
- Source: Web search results
- Relevance: Related to photography interest (visual arts)

### November 25, 2025

#### Workshops

**Holiday Cooking Class**

- Time: 2:00 PM - 5:00 PM
- Location: Culinary Institute Seattle
- Description: Traditional holiday recipes and techniques
- Source: Web search results
- Relevance: High match for cooking interest

**Fermentation Workshop**

- Time: 10:00 AM - 12:00 PM
- Location: Local Farm
- Description: Learn to make kimchi, sauerkraut, and kombucha
- Source: https://local-library.org/events
- Relevance: Related to cooking interest (food preparation)
```

## Troubleshooting

### Website Access Issues

If a website is inaccessible or returns errors, you should log the issue and continue with remaining websites rather than stopping the entire process.

### Pagination Detection Issues

If pagination links are not clearly identifiable or use JavaScript-based loading, you should attempt to identify URL patterns (e.g., ?page=2, /events/page/2) and try sequential page numbers until no more events are found.

### Rate Limiting

If a website blocks requests due to too many rapid page fetches, you should implement delays between requests and retry failed pages after a brief pause.

### No Events Found

If no events are found for a particular interest, you should expand search terms to include related activities and broader categories.

### Date Parsing Issues

If event dates are unclear or in non-standard formats, you should make reasonable assumptions and flag uncertain dates in the output for user review.
