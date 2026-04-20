"""AgentCore Browser client — CDP over SigV4-signed WebSocket.

Usage:
    from browser_client import AgentCoreBrowser

    browser = AgentCoreBrowser(browser_id="myBrowser-xxx", region="us-east-1")
    await browser.start("session_name")
    await browser.navigate("https://example.com")
    text = await browser.get_page_text()
    await browser.screenshot("/tmp/page.png")
    await browser.stop()
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from dataclasses import dataclass, field
from urllib.parse import urlparse

import boto3
import websockets
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

from config import REGION, SESSION_TIMEOUT_SECONDS, VIEWPORT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CDPResult:
    id: int
    result: dict = field(default_factory=dict)
    error: dict | None = None
    session_id: str | None = None


class AgentCoreBrowser:
    """Manages an AgentCore Browser session and exposes CDP commands."""

    def __init__(
        self,
        browser_id: str,
        region: str = REGION,
        viewport: dict | None = None,
        timeout: int = SESSION_TIMEOUT_SECONDS,
    ):
        self._browser_id = browser_id
        self._region = region
        self._viewport = viewport or VIEWPORT
        self._timeout = timeout
        self._control = boto3.client("bedrock-agentcore-control", region_name=region)
        self._data = boto3.client("bedrock-agentcore", region_name=region)
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._session_id: str | None = None
        self._cdp_session_id: str | None = None
        self._msg_id = 0

    # -- lifecycle --------------------------------------------------------

    @classmethod
    def create_browser(
        cls, name: str, region: str = REGION, network_mode: str = "PUBLIC",
    ) -> str:
        """Create a new browser resource and return its browser_id."""
        control = boto3.client("bedrock-agentcore-control", region_name=region)
        resp = control.create_browser(
            name=name,
            description=f"AgentCore Browser: {name}",
            networkConfiguration={"networkMode": network_mode},
        )
        browser_id = resp["browserId"]
        logger.info("Browser created: %s (arn: %s)", browser_id, resp["browserArn"])
        return browser_id

    @classmethod
    def list_browsers(cls, region: str = REGION) -> list[dict]:
        """List existing browser resources."""
        control = boto3.client("bedrock-agentcore-control", region_name=region)
        return control.list_browsers().get("browserSummaries", [])

    async def start(self, name: str = "session") -> str:
        """Start a browser session, connect WebSocket, attach to page target."""
        resp = self._data.start_browser_session(
            browserIdentifier=self._browser_id,
            name=name,
            sessionTimeoutSeconds=self._timeout,
            viewPort=self._viewport,
        )
        self._session_id = resp["sessionId"]
        ws_url = resp["streams"]["automationStream"]["streamEndpoint"]
        logger.info("Session %s started", self._session_id)

        headers = self._sign_ws(ws_url)
        self._ws = await websockets.connect(
            ws_url,
            additional_headers=headers,
            ping_interval=20,
            max_size=50 * 1024 * 1024,
        )

        targets = await self._send("Target.getTargets")
        page = next(t for t in targets.result["targetInfos"] if t["type"] == "page")
        attach = await self._send(
            "Target.attachToTarget",
            {"targetId": page["targetId"], "flatten": True},
        )
        self._cdp_session_id = attach.result["sessionId"]
        await self._send("Page.enable", session_id=self._cdp_session_id)
        await self._send("Runtime.enable", session_id=self._cdp_session_id)
        return self._session_id

    async def stop(self) -> None:
        """Close WebSocket and stop the browser session."""
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._session_id:
            self._data.stop_browser_session(
                browserIdentifier=self._browser_id,
                sessionId=self._session_id,
            )
            logger.info("Session %s stopped", self._session_id)
            self._session_id = None

    # -- navigation -------------------------------------------------------

    async def navigate(self, url: str, wait: float = 2.0) -> CDPResult:
        """Navigate to a URL and wait for initial load."""
        result = await self._send(
            "Page.navigate", {"url": url}, session_id=self._cdp_session_id,
        )
        await asyncio.sleep(wait)
        return result

    async def wait_for_selector(self, selector: str, timeout: float = 10.0) -> bool:
        """Poll until a CSS selector matches an element on the page."""
        interval = 0.5
        elapsed = 0.0
        while elapsed < timeout:
            found = await self.evaluate(
                f"!!document.querySelector('{selector}')"
            )
            if found:
                return True
            await asyncio.sleep(interval)
            elapsed += interval
        return False

    # -- evaluation -------------------------------------------------------

    async def evaluate(self, expression: str):
        """Run JavaScript in the page and return the result value."""
        result = await self._send(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True},
            session_id=self._cdp_session_id,
        )
        return result.result.get("result", {}).get("value")

    # -- interaction ------------------------------------------------------

    async def click(self, selector: str) -> None:
        """Click an element by CSS selector."""
        await self.evaluate(f"document.querySelector('{selector}').click()")

    async def type_text(self, selector: str, text: str) -> None:
        """Type text character-by-character via CDP Input.dispatchKeyEvent."""
        await self.evaluate(f"document.querySelector('{selector}').focus()")
        await self.evaluate(f"document.querySelector('{selector}').value = ''")
        for char in text:
            key_code = f"Key{char.upper()}" if char.isalpha() else ""
            await self._send(
                "Input.dispatchKeyEvent",
                {"type": "keyDown", "text": char, "key": char, "code": key_code},
                session_id=self._cdp_session_id,
            )
            await self._send(
                "Input.dispatchKeyEvent",
                {"type": "keyUp", "key": char, "code": key_code},
                session_id=self._cdp_session_id,
            )

    async def select_option(self, selector: str, value: str) -> None:
        """Select a dropdown option by value."""
        escaped = value.replace("'", "\\'")
        await self.evaluate(
            f"const el = document.querySelector('{selector}');"
            f"el.value = '{escaped}';"
            f"el.dispatchEvent(new Event('change', {{bubbles: true}}));"
        )

    # -- data extraction --------------------------------------------------

    async def get_text(self, selector: str) -> str | None:
        """Get innerText of an element."""
        return await self.evaluate(
            f"document.querySelector('{selector}')?.innerText"
        )

    async def get_page_text(self) -> str | None:
        """Get full visible text of the page."""
        return await self.evaluate("document.body.innerText")

    async def get_html(self, selector: str = "html") -> str | None:
        """Get outerHTML of an element."""
        return await self.evaluate(
            f"document.querySelector('{selector}')?.outerHTML"
        )

    async def get_url(self) -> str | None:
        """Get the current page URL."""
        return await self.evaluate("window.location.href")

    async def get_title(self) -> str | None:
        """Get the current page title."""
        return await self.evaluate("document.title")

    # -- capture ----------------------------------------------------------

    async def screenshot(self, path: str | None = None) -> bytes:
        """Capture a PNG screenshot. Optionally save to path."""
        result = await self._send(
            "Page.captureScreenshot",
            {"format": "png"},
            session_id=self._cdp_session_id,
        )
        data = base64.b64decode(result.result["data"])
        if path:
            with open(path, "wb") as f:
                f.write(data)
            logger.info("Screenshot saved to %s (%d bytes)", path, len(data))
        return data

    # -- cleanup ----------------------------------------------------------

    def destroy_browser(self) -> None:
        """Delete the browser resource entirely."""
        self._control.delete_browser(browserIdentifier=self._browser_id)
        logger.info("Browser %s deleted", self._browser_id)

    # -- internal ---------------------------------------------------------

    def _sign_ws(self, ws_url: str) -> dict:
        session = boto3.Session()
        creds = session.get_credentials().get_frozen_credentials()
        parsed = urlparse(ws_url)
        req = AWSRequest(method="GET", url=ws_url, headers={"host": parsed.netloc})
        SigV4Auth(creds, "bedrock-agentcore", self._region).add_auth(req)
        return dict(req.headers)

    async def _send(
        self,
        method: str,
        params: dict | None = None,
        session_id: str | None = None,
    ) -> CDPResult:
        self._msg_id += 1
        msg: dict = {"id": self._msg_id, "method": method}
        if params:
            msg["params"] = params
        if session_id:
            msg["sessionId"] = session_id

        await self._ws.send(json.dumps(msg))

        while True:
            raw = await asyncio.wait_for(self._ws.recv(), timeout=30)
            data = json.loads(raw)
            if data.get("id") == self._msg_id:
                return CDPResult(
                    id=data["id"],
                    result=data.get("result", {}),
                    error=data.get("error"),
                    session_id=data.get("sessionId"),
                )
