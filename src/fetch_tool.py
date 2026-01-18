"""
Simple fetch tool wrapping strands_tools.http_request.
"""

from strands import tool
from strands_tools.http_request import http_request
from typing import Dict, Any
import markdownify
import readabilipy.simple_json


def extract_content_from_html(html: str) -> str:
    """Extract and convert HTML content to Markdown format."""
    # Try readability first for article-style content
    ret = readabilipy.simple_json.simple_json_from_html_string(
        html, use_readability=True
    )
    
    # If readability extracted content, use it
    if ret["content"]:
        content = markdownify.markdownify(
            ret["content"],
            heading_style=markdownify.ATX,
        )
        # Check if content is suspiciously short (< 1000 chars) - might have stripped important content
        if len(content) > 1000:
            return content
    
    # Fall back to converting full HTML without readability
    # This preserves event listings, tables, and other structured content
    content = markdownify.markdownify(
        html,
        heading_style=markdownify.ATX,
        strip=['script', 'style', 'nav', 'footer', 'noscript', 'iframe']
    )
    return content


@tool
def fetch(url: str, convert_to_markdown: bool = True) -> Dict[str, Any]:
    """
    Fetch a URL and optionally convert to markdown.
    
    Args:
        url: URL to fetch
        convert_to_markdown: Convert HTML to markdown (default: True)
    
    Returns:
        Dict with status and content
    """
    # Call http_request tool with GET method
    # http_request expects a ToolUse dict with input
    tool_use = {
        "input": {
            "method": "GET",
            "url": url,
            "convert_to_markdown": convert_to_markdown
        }
    }
    
    result = http_request(tool_use)
    
    # http_request returns a ToolResult with status and content
    # Extract the body from the content array
    if result.get("status") == "success":
        content_items = result.get("content", [])
        # Find the body content (it's in the item with "Body:" prefix)
        body = ""
        for item in content_items:
            text = item.get("text", "")
            if text.startswith("Body: "):
                body = text[6:]  # Remove "Body: " prefix
                break
        
        # If markdown conversion was requested but http_request didn't do it, do it now
        if convert_to_markdown and not tool_use["input"].get("convert_to_markdown"):
            try:
                body = extract_content_from_html(body)
            except:
                pass
        
        return {
            "status": "success",
            "content": [{"text": f"Contents of {url}:\n{body}"}]
        }
    else:
        return result
