"""
Browser automation service for ARLI agents
Wraps Hermes browser tools for web scraping and automation
"""
import os
import json
from typing import Dict, Optional, Any
from dataclasses import dataclass

# Try to import Hermes browser tools
try:
    from hermes_tools import browser_navigate, browser_snapshot, browser_click, browser_type, browser_press
    HERMES_BROWSER_AVAILABLE = True
except ImportError:
    HERMES_BROWSER_AVAILABLE = False


@dataclass
class BrowserActionResult:
    success: bool
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    screenshot_path: Optional[str] = None
    error: Optional[str] = None


class BrowserService:
    """Service for agent-controlled browser automation"""

    def __init__(self):
        self.current_url: Optional[str] = None
        self.session_active = False

    async def navigate(self, url: str) -> BrowserActionResult:
        """Navigate to a URL"""
        if not HERMES_BROWSER_AVAILABLE:
            return BrowserActionResult(
                success=False,
                error="Browser automation not available. Install Hermes browser tools.",
            )
        try:
            # browser_navigate may be sync or async depending on Hermes implementation
            result = browser_navigate(url=url)
            self.current_url = url
            self.session_active = True
            return BrowserActionResult(success=True, url=url)
        except Exception as e:
            return BrowserActionResult(success=False, error=str(e))

    async def get_page_content(self, full: bool = False) -> BrowserActionResult:
        """Get current page content via snapshot"""
        if not HERMES_BROWSER_AVAILABLE:
            return BrowserActionResult(success=False, error="Browser not available")
        try:
            result = browser_snapshot(full=full)
            # result is a dict with snapshot info
            content = result.get("snapshot", "") if isinstance(result, dict) else str(result)
            return BrowserActionResult(
                success=True,
                url=self.current_url,
                content=content[:8000] if not full else content,
            )
        except Exception as e:
            return BrowserActionResult(success=False, error=str(e))

    async def click(self, ref: str) -> BrowserActionResult:
        """Click an element by ref ID"""
        if not HERMES_BROWSER_AVAILABLE:
            return BrowserActionResult(success=False, error="Browser not available")
        try:
            result = browser_click(ref=ref)
            return BrowserActionResult(success=True, url=self.current_url)
        except Exception as e:
            return BrowserActionResult(success=False, error=str(e))

    async def type_text(self, ref: str, text: str) -> BrowserActionResult:
        """Type text into an input field"""
        if not HERMES_BROWSER_AVAILABLE:
            return BrowserActionResult(success=False, error="Browser not available")
        try:
            result = browser_type(ref=ref, text=text)
            return BrowserActionResult(success=True, url=self.current_url)
        except Exception as e:
            return BrowserActionResult(success=False, error=str(e))

    async def press_key(self, key: str) -> BrowserActionResult:
        """Press a keyboard key"""
        if not HERMES_BROWSER_AVAILABLE:
            return BrowserActionResult(success=False, error="Browser not available")
        try:
            result = browser_press(key=key)
            return BrowserActionResult(success=True, url=self.current_url)
        except Exception as e:
            return BrowserActionResult(success=False, error=str(e))

    async def research(self, query: str, sources: Optional[list] = None) -> Dict[str, Any]:
        """
        Perform a simple research task:
        1. Search DuckDuckGo/Google
        2. Open top result
        3. Extract key content
        """
        import asyncio
        search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
        
        nav = await self.navigate(search_url)
        if not nav.success:
            return {"success": False, "error": nav.error}
        
        await asyncio.sleep(2)  # Let page load
        content = await self.get_page_content()
        
        return {
            "success": True,
            "query": query,
            "url": search_url,
            "extracted_content": content.content[:5000] if content.success else None,
            "error": content.error if not content.success else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_url": self.current_url,
            "session_active": self.session_active,
            "browser_available": HERMES_BROWSER_AVAILABLE,
        }
