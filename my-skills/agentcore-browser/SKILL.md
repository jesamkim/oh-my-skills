---
name: agentcore-browser
description: |
  AWS Bedrock AgentCore Browser automation using CDP (Chrome DevTools Protocol) over
  SigV4-signed WebSocket. Python-native, no local Chrome needed — the browser runs
  as a managed AWS service. Use this skill as a complement/fallback to agent-browser:
  when agent-browser CLI is unavailable, when there is no local Chrome on a headless
  server, when Python-native async browser control is preferred, when accessing sites
  inside an AWS VPC, or when the user explicitly mentions "AgentCore browser",
  "AWS headless browser", "managed browser", or "CDP on Bedrock".
  Also trigger when agent-browser fails due to missing Chrome, display issues,
  or environment constraints, and the user wants an alternative approach.
license: MIT License
metadata:
    skill-author: jesamkim
    version: 1.0.0
allowed-tools: [Read, Write, Edit, Bash, Grep, Glob]
---

# AgentCore Browser — CDP over AWS Managed Chrome

Automate a cloud-hosted Chrome 144 browser through Bedrock AgentCore.
The browser runs entirely on AWS — no local Chrome, no X server, no Playwright install.
You talk to it via CDP commands over a SigV4-authenticated WebSocket.

## When to Use This Skill vs agent-browser

**Try agent-browser first.** It is faster (local execution, no network RTT) and free.
Switch to this skill when:

| Situation | Why this skill wins |
|-----------|-------------------|
| No local Chrome / headless server | Browser runs on AWS, nothing to install |
| agent-browser CLI not installed | Only needs `boto3` + `websockets` (Python) |
| Python agent pipeline (Strands, LangGraph) | Native async/await, no shell subprocess |
| AWS VPC-internal sites | VPC network mode reaches private ALBs |
| Need session persistence across runs | Browser Profile API saves cookies/storage |
| agent-browser `--headed` display issues | Not applicable — always headless on AWS |

## Prerequisites

```bash
pip install boto3 websockets
```

AWS credentials must have `bedrock-agentcore:*` and `bedrock-agentcore-control:*` permissions.

## Quick Start

### Step 0: Create a Browser Resource (one-time)

```python
import boto3
control = boto3.client("bedrock-agentcore-control", region_name="us-east-1")
resp = control.create_browser(
    name="myBrowser",
    description="Experiment browser",
    networkConfiguration={"networkMode": "PUBLIC"},
)
browser_id = resp["browserId"]  # e.g. "myBrowser-O9bw0JnQyc"
```

Or use the helper:

```python
from scripts.browser_client import AgentCoreBrowser
browser_id = AgentCoreBrowser.create_browser("myBrowser", region="us-east-1")
```

### Step 1: Connect and Navigate

```python
import asyncio
from scripts.browser_client import AgentCoreBrowser

async def main():
    browser = AgentCoreBrowser(browser_id="myBrowser-xxxxx", region="us-east-1")
    await browser.start("my_session")

    await browser.navigate("https://example.com")
    title = await browser.get_title()
    print(f"Page title: {title}")

    await browser.screenshot("/tmp/page.png")
    await browser.stop()

asyncio.run(main())
```

## Core Workflow

Every automation follows this pattern:

1. **Navigate** — `await browser.navigate(url)`
2. **Extract** — `await browser.evaluate(js)` or `await browser.get_page_text()`
3. **Interact** — `await browser.click(selector)` / `await browser.type_text(selector, text)`
4. **Capture** — `await browser.screenshot(path)`
5. **Stop** — `await browser.stop()` (always call this to avoid charges)

## API Reference

### Lifecycle

| Method | Description |
|--------|-------------|
| `AgentCoreBrowser.create_browser(name, region)` | Create a browser resource (class method, one-time) |
| `AgentCoreBrowser.list_browsers(region)` | List existing browser resources |
| `browser.start(name)` | Start session, connect WebSocket, attach to page |
| `browser.stop()` | Close WebSocket and stop session |
| `browser.destroy_browser()` | Delete the browser resource |

### Navigation

| Method | Description |
|--------|-------------|
| `navigate(url, wait=2.0)` | Go to URL, wait for load |
| `wait_for_selector(selector, timeout=10)` | Poll until element exists |

### Data Extraction

| Method | Description |
|--------|-------------|
| `evaluate(expression)` | Run JavaScript, return value |
| `get_text(selector)` | Get element's innerText |
| `get_page_text()` | Get full page text |
| `get_html(selector)` | Get element's outerHTML |
| `get_url()` | Current page URL |
| `get_title()` | Current page title |

### Interaction

| Method | Description |
|--------|-------------|
| `click(selector)` | Click element by CSS selector |
| `type_text(selector, text)` | Type text char-by-char (CDP key events) |
| `select_option(selector, value)` | Select dropdown option |

### Capture

| Method | Description |
|--------|-------------|
| `screenshot(path=None)` | PNG screenshot, optionally save to file |

## Patterns

### Form Submission

```python
await browser.navigate("https://httpbin.org/forms/post")
await browser.type_text('input[name="custname"]', "Test User")
await browser.type_text('input[name="custemail"]', "test@example.com")
await browser.evaluate(
    "document.querySelector('input[name=\"size\"][value=\"medium\"]').checked = true"
)
await browser.evaluate("document.querySelector('form').submit()")
await asyncio.sleep(2)
result = await browser.get_page_text()
```

### Web Scraping (JS-rendered pages)

```python
await browser.navigate("https://finance.naver.com/marketindex/")
rate = await browser.evaluate(
    "document.querySelector('.head_info .value')?.innerText"
)
print(f"USD/KRW: {rate}")
```

### Wait for Dynamic Content

```python
await browser.navigate("https://spa-app.example.com")
found = await browser.wait_for_selector(".data-table", timeout=15)
if found:
    data = await browser.evaluate("document.querySelector('.data-table').innerText")
```

## Important Notes

### Cost Management
Sessions are billed by duration. Always call `browser.stop()` in a `finally` block:

```python
browser = AgentCoreBrowser(browser_id="...", region="us-east-1")
try:
    await browser.start("task")
    # ... work ...
finally:
    await browser.stop()
```

### IP Restrictions
The browser runs on AWS IP ranges. Some sites block AWS IPs:
- weather.go.kr (Korean Met Administration) — returns error page
- accuweather.com — returns 403 Access Denied

Sites that work well from AWS:
- naver.com, finance.naver.com — fully functional
- httpbin.org — fully functional
- wttr.in — fully functional
- Most SaaS/enterprise tools — generally accessible

### Form Input
Setting `element.value = "..."` via JS alone does not trigger browser input events
on all form frameworks. The `type_text()` method uses CDP `Input.dispatchKeyEvent`
to simulate real keystroke events, which works reliably across React, Vue, and plain HTML forms.

### CDP Protocol
The automation stream speaks **Chrome DevTools Protocol v1.3** (JSON-RPC over WebSocket).
Any CDP command works — the methods above are convenience wrappers. For advanced use:

```python
result = await browser._send(
    "Network.enable", session_id=browser._cdp_session_id
)
```

### Browser Profile Persistence
Save and restore session state (cookies, localStorage) across sessions:

```python
# Save after login
client = boto3.client("bedrock-agentcore", region_name="us-east-1")
client.save_browser_session_profile(
    profileIdentifier="my_profile",
    browserIdentifier=browser_id,
    sessionId=session_id,
)

# Reuse in next session
resp = client.start_browser_session(
    browserIdentifier=browser_id,
    name="resumed",
    profileConfiguration={"profileIdentifier": "my_profile"},
    ...
)
```
