"""
Custom browser tool for serendipity agent with modified wait strategy.
"""

import asyncio
import logging
import os
from typing import Any, Dict

import nest_asyncio
import markdownify
import readabilipy.simple_json
from playwright.async_api import async_playwright
from strands import tool

logger = logging.getLogger(__name__)


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


class SerendipityBrowser:
    """Custom browser tool with domcontentloaded wait strategy."""
    
    def __init__(self):
        self._playwright = None
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        nest_asyncio.apply()
    
    @tool
    def browser_fetch(
        self,
        url: str,
        max_length: int = 5000,
        start_index: int = 0,
        raw: bool = False,
        wait_seconds: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch a URL using a browser with JavaScript support and optionally extract contents as markdown.
        
        This tool uses a real browser to handle JavaScript-heavy pages that don't work with regular fetch.
        
        Args:
            url: URL to fetch
            max_length: Maximum number of characters to return (default: 5000)
            start_index: Start output at this character index (default: 0)
            raw: Get actual HTML content without simplification to markdown (default: False)
            wait_seconds: Seconds to wait after page load for JavaScript to execute (default: 10)
        
        Returns:
            Dict with status and content
        """
        return self._execute_async(self._fetch(url, max_length, start_index, raw, wait_seconds))
    
    async def _fetch(self, url: str, max_length: int, start_index: int, raw: bool, wait_seconds: int) -> Dict[str, Any]:
        """Fetch URL with browser."""
        browser = None
        try:
            # Start playwright if needed
            if not self._playwright:
                self._playwright = await async_playwright().start()
            
            # Get launch args from environment
            launch_args = os.getenv("PLAYWRIGHT_CHROMIUM_ARGS", "").split()
            
            # Launch browser
            browser = await self._playwright.chromium.launch(
                headless=os.getenv("STRANDS_BROWSER_HEADLESS", "false").lower() == "true",
                args=launch_args if launch_args else None
            )
            
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate with domcontentloaded
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for JavaScript
            await asyncio.sleep(wait_seconds)
            
            # Get HTML
            html = await page.content()
            
            # Close browser
            await browser.close()
            
            # Convert to markdown unless raw requested
            if raw:
                content = html
            else:
                content = extract_content_from_html(html)
            
            # Handle pagination
            original_length = len(content)
            if start_index >= original_length:
                content = "<error>No more content available.</error>"
            else:
                truncated_content = content[start_index : start_index + max_length]
                if not truncated_content:
                    content = "<error>No more content available.</error>"
                else:
                    content = truncated_content
                    actual_content_length = len(truncated_content)
                    remaining_content = original_length - (start_index + actual_content_length)
                    if actual_content_length == max_length and remaining_content > 0:
                        next_start = start_index + actual_content_length
                        content += f"\n\n<error>Content truncated. Call browser_fetch with start_index={next_start} to get more content.</error>"
            
            return {
                "status": "success",
                "content": [{"text": f"Contents of {url}:\n{content}"}]
            }
            
        except Exception as e:
            logger.error(f"Browser fetch failed: {e}")
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            return {
                "status": "error",
                "content": [{"text": f"Error: {str(e)}"}]
            }
    
    def _execute_async(self, coro) -> Any:
        """Execute async coroutine in event loop."""
        return self._loop.run_until_complete(coro)
    
    async def cleanup(self):
        """Cleanup playwright."""
        if self._playwright:
            try:
                await self._playwright.stop()
            except:
                pass
            self._playwright = None
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self._execute_async(self.cleanup())
        except:
            pass
