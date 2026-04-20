#!/usr/bin/env python3
"""
Bedrock Computer Use Agent v3.0
- Model-aware tool version auto-detection (supports 3.5 through 4.6)
- Pre-planning: model plans subtasks before executing
- Batch execution: multiple actions per turn, screenshot only on last action
- Context compression: old screenshots replaced with text summaries
- Intelligent retry with exponential backoff for transient errors
"""

import argparse
import io
import os
import random
import subprocess
import tempfile
import time
from dataclasses import dataclass

import boto3
import pyautogui
from botocore.exceptions import ClientError
from PIL import Image

# Safety: move mouse to corner to abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

DEFAULT_MODEL = "global.anthropic.claude-opus-4-6-v1"
DEFAULT_REGION = "us-west-2"
DEFAULT_MAX_STEPS = 50
ACTION_DELAY = 0.5
MAX_RETRIES = 3
MAX_CONTEXT_TURNS = 10  # keep last N turn-pairs (assistant+user), compress older ones

TARGET_WIDTH = 1280
TARGET_HEIGHT = 800

SYSTEM_PROMPT = (
    "You are a desktop GUI automation agent on macOS. You can see the screen via "
    "screenshots and control the computer via mouse/keyboard actions.\n\n"
    "## Planning & Efficiency\n"
    "Before taking any action, briefly plan the full sequence of steps needed to "
    "complete the task. Then execute multiple actions in a single turn whenever "
    "the sequence is predictable (e.g., click a field, then type text, then press Enter). "
    "Only request a screenshot when you need to verify an outcome or discover "
    "new UI elements you haven't seen yet. This drastically reduces wasted turns.\n\n"
    "Example — searching in Spotlight:\n"
    "  BAD:  Turn 1: key Cmd+Space → Turn 2: (screenshot) → Turn 3: type 'Safari' → Turn 4: (screenshot) → Turn 5: key Enter\n"
    "  GOOD: Turn 1: key Cmd+Space, type 'Safari', key Enter (3 actions, 1 turn)\n\n"
    "## Guidelines\n"
    "- Before clicking, describe what you see and identify the target element clearly.\n"
    "- If an action didn't produce the expected result, try an alternative approach.\n"
    "- For text input, verify the field is focused before typing.\n"
    "- Report your reasoning briefly at each step.\n"
    "- If you're stuck after 3 attempts on the same action, explain why and stop.\n"
    "- Be precise with coordinates — click the center of UI elements, not edges.\n\n"
    "macOS — escaping a full-screen terminal app:\n"
    "If the menu bar (Apple icon at top-left) is NOT visible, the app is full-screen. "
    "Follow these exact steps to escape and open another app:\n"
    "  Step A: Press Ctrl+Cmd+F to exit full-screen mode.\n"
    "  Step B: Click on the desktop background (any empty area) to give Finder focus.\n"
    "  Step C: Press Cmd+Space to open Spotlight. Type the app name and press Enter.\n"
    "If the menu bar IS already visible, skip Step A and go directly to Step B.\n\n"
    "macOS — Dock and Finder:\n"
    "- The Dock may be at bottom, left, or right edge, and may auto-hide.\n"
    "- Finder icon (blue smiley face) is always the first Dock item.\n"
    "- Cmd+Tab switches between running apps.\n"
    "- In Finder, use the sidebar (Downloads, Documents, Desktop) or "
    "Cmd+Shift+G to type a path like ~/Downloads.\n\n"
    "macOS — input method (CRITICAL):\n"
    "- Check the menu bar for the input source indicator (e.g., 'ABC', '2-Set Korean', "
    "or a flag icon). If it shows a non-English input method, you MUST switch to "
    "English BEFORE typing any commands or URLs.\n"
    "- To switch input method: press Ctrl+Space or Caps Lock (depends on user config). "
    "Verify the indicator changes to 'ABC' before typing.\n"
    "- If typing produces unexpected characters (Korean, Japanese, etc.), "
    "press Escape to clear, switch input method, then retype.\n\n"
    "macOS — things to AVOID:\n"
    "- Never move the mouse to any screen corner (0,0), (max,0), (0,max), (max,max). "
    "macOS Hot Corners can trigger screen lock, screensaver, or Mission Control.\n"
    "- Never try to click the Spotlight magnifying glass icon in the menu bar. "
    "The icons are tiny and easy to misclick. Always use Cmd+Space instead.\n"
    "- If you accidentally trigger the lock screen or screensaver, you cannot "
    "recover (no password access). Report the issue and stop."
)


# ---------------------------------------------------------------------------
# Model configuration: auto-detect tool versions based on model ID
# ---------------------------------------------------------------------------

@dataclass
class ModelConfig:
    computer_type: str
    bash_type: str
    editor_type: str
    editor_name: str
    beta: list[str]
    generation: str


def detect_model_config(model_id: str) -> ModelConfig:
    """Auto-detect tool versions and beta headers from model ID."""
    m = model_id.lower()

    # Claude 4.6 generation (Opus 4.6, Sonnet 4.6)
    if "opus-4-6" in m or "sonnet-4-6" in m or "claude-4-6" in m:
        return ModelConfig(
            computer_type="computer_20251124",
            bash_type="bash_20250124",
            editor_type="text_editor_20250728",
            editor_name="str_replace_based_edit_tool",
            beta=["computer-use-2025-11-24"],
            generation="4.6",
        )

    # Claude Opus 4.5
    if "opus-4-5" in m:
        return ModelConfig(
            computer_type="computer_20250124",
            bash_type="bash_20250124",
            editor_type="text_editor_20250728",
            editor_name="str_replace_based_edit_tool",
            beta=["computer-use-2025-01-24"],
            generation="4.5",
        )

    # Claude Sonnet 4.5, Haiku 4.5
    if "sonnet-4-5" in m or "haiku-4-5" in m:
        return ModelConfig(
            computer_type="computer_20250124",
            bash_type="bash_20250124",
            editor_type="text_editor_20250124",
            editor_name="str_replace_editor",
            beta=["computer-use-2025-01-24"],
            generation="4.5",
        )

    # Claude Opus 4.1, Sonnet 4.0 (Bedrock ID: claude-sonnet-4-20250514)
    if "opus-4-1" in m or "sonnet-4-0" in m or "sonnet-4-2025" in m:
        return ModelConfig(
            computer_type="computer_20250124",
            bash_type="bash_20250124",
            editor_type="text_editor_20250124",
            editor_name="str_replace_editor",
            beta=["computer-use-2025-01-24"],
            generation="4.x",
        )

    # Claude 3.5 Sonnet v2 (legacy)
    if "3-5-sonnet" in m or "3.5-sonnet" in m:
        return ModelConfig(
            computer_type="computer_20241022",
            bash_type="bash_20241022",
            editor_type="text_editor_20241022",
            editor_name="str_replace_editor",
            beta=["computer-use-2024-10-22"],
            generation="3.5",
        )

    # Fallback: assume 4.5-compatible
    print(f"  [warn] Unknown model '{model_id}', defaulting to 4.5 tool versions")
    return ModelConfig(
        computer_type="computer_20250124",
        bash_type="bash_20250124",
        editor_type="text_editor_20250124",
        editor_name="str_replace_editor",
        beta=["computer-use-2025-01-24"],
        generation="unknown",
    )


# ---------------------------------------------------------------------------
# Screenshot capture
# ---------------------------------------------------------------------------

def capture_screenshot() -> bytes:
    """Capture screenshot on macOS using screencapture, return PNG bytes."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ["screencapture", "-x", "-C", tmp_path],
            check=True,
            capture_output=True,
        )
        img = Image.open(tmp_path)
        img.load()  # force pixel data into memory before deleting file
    finally:
        os.unlink(tmp_path)

    if img.width > TARGET_WIDTH or img.height > TARGET_HEIGHT:
        img.thumbnail((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def get_screen_size() -> tuple[int, int]:
    size = pyautogui.size()
    return size.width, size.height


def scale_coordinates(x: int, y: int, screen_w: int, screen_h: int) -> tuple[int, int]:
    scale_x = screen_w / TARGET_WIDTH
    scale_y = screen_h / TARGET_HEIGHT
    return int(x * scale_x), int(y * scale_y)


# ---------------------------------------------------------------------------
# Action execution
# ---------------------------------------------------------------------------

def execute_action(action: str, tool_input: dict, screen_w: int, screen_h: int) -> str:
    """Execute a computer use action and return a text result."""
    time.sleep(ACTION_DELAY)

    if action == "screenshot":
        return "__screenshot__"

    elif action == "left_click":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> left_click at ({coords[0]},{coords[1]}) -> screen ({sx},{sy})")
        pyautogui.click(sx, sy)
        return f"Clicked at ({sx}, {sy})"

    elif action == "right_click":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> right_click at ({coords[0]},{coords[1]}) -> screen ({sx},{sy})")
        pyautogui.rightClick(sx, sy)
        return f"Right-clicked at ({sx}, {sy})"

    elif action == "double_click":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> double_click at ({coords[0]},{coords[1]}) -> screen ({sx},{sy})")
        pyautogui.doubleClick(sx, sy)
        return f"Double-clicked at ({sx}, {sy})"

    elif action == "triple_click":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> triple_click at ({sx},{sy})")
        pyautogui.click(sx, sy, clicks=3)
        return f"Triple-clicked at ({sx}, {sy})"

    elif action == "mouse_move":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> mouse_move to ({coords[0]},{coords[1]}) -> screen ({sx},{sy})")
        pyautogui.moveTo(sx, sy)
        return f"Moved mouse to ({sx}, {sy})"

    elif action == "left_click_drag":
        start = tool_input.get("start_coordinate", [0, 0])
        end = tool_input.get("coordinate", [0, 0])
        sx1, sy1 = scale_coordinates(start[0], start[1], screen_w, screen_h)
        sx2, sy2 = scale_coordinates(end[0], end[1], screen_w, screen_h)
        print(f"  -> drag from ({sx1},{sy1}) to ({sx2},{sy2})")
        pyautogui.moveTo(sx1, sy1)
        pyautogui.mouseDown()
        pyautogui.moveTo(sx2, sy2, duration=0.5)
        pyautogui.mouseUp()
        return f"Dragged from ({sx1},{sy1}) to ({sx2},{sy2})"

    elif action == "type":
        text = tool_input.get("text", "")
        print(f"  -> type: {text[:50]}{'...' if len(text) > 50 else ''}")
        if text.isascii():
            pyautogui.typewrite(text, interval=0.02)
        else:
            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
            pyautogui.hotkey("command", "v")
        return f"Typed: {text}"

    elif action == "key":
        key = tool_input.get("text", "")
        print(f"  -> key: {key}")
        keys = key.lower().split("+")
        if len(keys) > 1:
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys[0])
        return f"Pressed key: {key}"

    elif action in ("scroll", "scroll_up", "scroll_down"):
        coords = tool_input.get("coordinate", [TARGET_WIDTH // 2, TARGET_HEIGHT // 2])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        amount = tool_input.get("amount", 3)
        # "scroll" action uses direction from model; scroll_down/scroll_up are legacy
        if action == "scroll_down" or (action == "scroll" and tool_input.get("direction") == "down"):
            direction = -amount
        else:
            direction = amount
        label = "down" if direction < 0 else "up"
        print(f"  -> scroll {label} by {amount} at ({sx},{sy})")
        pyautogui.scroll(direction, sx, sy)
        return f"Scrolled {label} by {amount}"

    elif action == "hold_key":
        key = tool_input.get("key", "")
        duration = min(tool_input.get("duration", 0.5), 10.0)
        print(f"  -> hold_key: {key} for {duration}s")
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        return f"Held key {key} for {duration}s"

    elif action == "left_mouse_down":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> mouse_down at ({sx},{sy})")
        pyautogui.moveTo(sx, sy)
        pyautogui.mouseDown()
        return f"Mouse down at ({sx}, {sy})"

    elif action == "left_mouse_up":
        coords = tool_input.get("coordinate", [0, 0])
        sx, sy = scale_coordinates(coords[0], coords[1], screen_w, screen_h)
        print(f"  -> mouse_up at ({sx},{sy})")
        pyautogui.moveTo(sx, sy)
        pyautogui.mouseUp()
        return f"Mouse up at ({sx}, {sy})"

    elif action == "wait":
        duration = min(tool_input.get("duration", 1), 30.0)
        print(f"  -> wait {duration}s")
        time.sleep(duration)
        return f"Waited {duration} seconds"

    else:
        print(f"  -> unknown action: {action}")
        return f"Unknown action: {action}"


# ---------------------------------------------------------------------------
# Tool result builder
# ---------------------------------------------------------------------------

def build_tool_result(tool_use_id: str, action_result: str, screenshot_bytes: bytes | None = None) -> dict:
    if action_result == "__screenshot__" and screenshot_bytes:
        return {
            "toolResult": {
                "toolUseId": tool_use_id,
                "content": [
                    {
                        "image": {
                            "format": "png",
                            "source": {"bytes": screenshot_bytes},
                        }
                    }
                ],
            }
        }
    return {
        "toolResult": {
            "toolUseId": tool_use_id,
            "content": [{"text": action_result}],
        }
    }


# ---------------------------------------------------------------------------
# Retry logic
# ---------------------------------------------------------------------------

def is_transient_error(error: Exception) -> bool:
    """Classify whether an API error is transient (worth retrying)."""
    if isinstance(error, ClientError):
        code = error.response.get("Error", {}).get("Code", "")
        # Throttling, service unavailable, internal errors
        if code in ("ThrottlingException", "TooManyRequestsException",
                     "ServiceUnavailableException", "InternalServerException",
                     "ModelTimeoutException"):
            return True
        http_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)
        return http_code >= 500 or http_code == 429
    # Network / connection errors
    return "ConnectionError" in type(error).__name__ or "Timeout" in type(error).__name__


def call_with_retry(client, kwargs: dict) -> dict:
    """Call Bedrock Converse API with exponential backoff for transient errors."""
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.converse(**kwargs)
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES and is_transient_error(e):
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"  [retry {attempt + 1}/{MAX_RETRIES}] {type(e).__name__}: {e}")
                print(f"  Waiting {wait:.1f}s before retry...")
                time.sleep(wait)
            else:
                raise
    raise last_error  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Context compression: keep only recent screenshots, summarize older ones
# ---------------------------------------------------------------------------

def compress_context(messages: list[dict], max_turns: int = MAX_CONTEXT_TURNS) -> list[dict]:
    """Replace screenshots in old messages with text placeholders.

    A "turn" is an assistant+user message pair.  The first message (user's
    task + initial screenshot) is always preserved.  Among the remaining
    turn-pairs, only the most recent *max_turns* pairs keep their images;
    older images are replaced with '[screenshot omitted]'.
    """
    if len(messages) <= 1 + max_turns * 2:
        return messages  # nothing to compress

    # messages[0] = initial user message (always keep)
    # messages[1:] = alternating assistant, user pairs
    rest = messages[1:]
    # Number of messages to compress (keep last max_turns*2 messages intact)
    keep_count = max_turns * 2
    compress_end = len(rest) - keep_count

    if compress_end <= 0:
        return messages

    for i in range(compress_end):
        msg = rest[i]
        if not isinstance(msg.get("content"), list):
            continue
        new_content = []
        for block in msg["content"]:
            if "image" in block:
                new_content.append({"text": "[screenshot omitted]"})
            elif "toolResult" in block:
                tr = block["toolResult"]
                new_items = []
                for item in tr.get("content", []):
                    if "image" in item:
                        new_items.append({"text": "[screenshot omitted]"})
                    else:
                        new_items.append(item)
                new_content.append({
                    "toolResult": {
                        "toolUseId": tr["toolUseId"],
                        "content": new_items,
                    }
                })
            else:
                new_content.append(block)
        msg["content"] = new_content

    return messages


# ---------------------------------------------------------------------------
# Main agentic loop
# ---------------------------------------------------------------------------

def run_computer_use(task: str, model_id: str, region: str, max_steps: int,
                     no_bash: bool = False, no_editor: bool = False):
    client = boto3.client("bedrock-runtime", region_name=region)
    screen_w, screen_h = get_screen_size()
    config = detect_model_config(model_id)

    print(f"Screen size: {screen_w}x{screen_h}")
    print(f"Model: {model_id} (generation {config.generation})")
    print(f"Tool version: {config.computer_type}")
    print(f"Beta: {config.beta}")
    print(f"Bash tool: {'disabled' if no_bash else 'enabled'}")
    print(f"Editor tool: {'disabled' if no_editor else 'enabled'}")
    print(f"Task: {task}")
    print(f"Max steps: {max_steps}")
    print("-" * 60)

    # Initial screenshot
    print("[Step 0] Capturing initial screenshot...")
    screenshot = capture_screenshot()

    # System prompt for better guidance
    system = [{"text": SYSTEM_PROMPT}]

    messages = [
        {
            "role": "user",
            "content": [
                {"text": task},
                {
                    "image": {
                        "format": "png",
                        "source": {"bytes": screenshot},
                    }
                },
            ],
        }
    ]

    # Build tool configuration based on detected model version
    tools_list = [
        {
            "type": config.computer_type,
            "name": "computer",
            "display_height_px": TARGET_HEIGHT,
            "display_width_px": TARGET_WIDTH,
            "display_number": 0,
        },
    ]
    if not no_bash:
        tools_list.append({"type": config.bash_type, "name": "bash"})
    if not no_editor:
        tools_list.append({"type": config.editor_type, "name": config.editor_name})

    computer_use_tools = {
        "tools": tools_list,
        "anthropic_beta": config.beta,
    }

    # Bedrock Converse API requires toolConfig when toolResult blocks are present
    dummy_tool_config = {
        "tools": [{
            "toolSpec": {
                "name": "noop",
                "description": "placeholder for computer use tool results",
                "inputSchema": {"json": {"type": "object", "properties": {}}},
            }
        }]
    }

    has_tool_results = False
    total_input_tokens = 0
    total_output_tokens = 0

    for step in range(1, max_steps + 1):
        print(f"\n[Step {step}/{max_steps}] Calling Bedrock Converse API...")

        try:
            kwargs = {
                "modelId": model_id,
                "system": system,
                "messages": messages,
                "additionalModelRequestFields": computer_use_tools,
            }
            if has_tool_results:
                kwargs["toolConfig"] = dummy_tool_config

            response = call_with_retry(client, kwargs)
        except Exception as e:
            print(f"  API Error (non-retryable): {e}")
            break

        output_msg = response["output"]["message"]
        content_blocks = output_msg["content"]
        stop_reason = response.get("stopReason", "")
        usage = response.get("usage", {})

        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        print(f"  Stop reason: {stop_reason}")
        print(f"  Tokens - input: {input_tokens}, output: {output_tokens}")

        for block in content_blocks:
            if "text" in block:
                print(f"  Model: {block['text']}")

        if stop_reason == "end_turn":
            print("\n" + "=" * 60)
            print("Task completed!")
            print(f"Total tokens - input: {total_input_tokens}, output: {total_output_tokens}")
            break

        # Process tool_use blocks with batch optimization:
        # Only capture a verification screenshot after the LAST computer action,
        # not after every single one. This cuts redundant model-vision calls.
        tool_use_blocks = [b for b in content_blocks if "toolUse" in b]
        computer_indices = [
            i for i, b in enumerate(tool_use_blocks)
            if b["toolUse"]["name"] == "computer"
        ]
        last_computer_idx = computer_indices[-1] if computer_indices else -1

        tool_results = []
        for block_idx, block in enumerate(tool_use_blocks):
            tool_use = block["toolUse"]
            tool_use_id = tool_use["toolUseId"]
            tool_name = tool_use["name"]
            tool_input = tool_use.get("input", {})

            if tool_name == "computer":
                action = tool_input.get("action", "")
                is_last_computer = (block_idx == last_computer_idx)
                batch_label = "" if is_last_computer else " [batch]"
                print(f"  Action: {action}{batch_label}")

                result = execute_action(action, tool_input, screen_w, screen_h)

                if result == "__screenshot__":
                    new_screenshot = capture_screenshot()
                    tool_results.append(
                        build_tool_result(tool_use_id, result, new_screenshot)
                    )
                elif is_last_computer:
                    # Verification screenshot only on the last computer action
                    time.sleep(0.3)
                    new_screenshot = capture_screenshot()
                    tool_results.append(
                        build_tool_result(tool_use_id, "__screenshot__", new_screenshot)
                    )
                else:
                    # Mid-batch: text result only, no screenshot
                    tool_results.append(
                        build_tool_result(tool_use_id, result)
                    )

            elif tool_name == "bash":
                command = tool_input.get("command", "")
                print(f"  Bash: {command[:80]}")
                if no_bash:
                    tool_results.append(
                        build_tool_result(tool_use_id, "Bash tool is disabled (--no-bash)")
                    )
                    continue
                try:
                    proc = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    output = proc.stdout + proc.stderr
                    tool_results.append(
                        build_tool_result(tool_use_id, output or "(no output)")
                    )
                except subprocess.TimeoutExpired:
                    tool_results.append(
                        build_tool_result(tool_use_id, "Command timed out after 30s")
                    )

            elif tool_name in ("str_replace_based_edit_tool", "str_replace_editor"):
                command = tool_input.get("command", "")
                path = tool_input.get("path", "")
                print(f"  Editor: {command} {path}")

                if no_editor:
                    tool_results.append(
                        build_tool_result(tool_use_id, "Editor tool is disabled (--no-editor)")
                    )
                    continue

                if command == "view":
                    try:
                        with open(path, "r") as f:
                            content = f.read()
                        tool_results.append(
                            build_tool_result(tool_use_id, content[:5000])
                        )
                    except Exception as e:
                        tool_results.append(
                            build_tool_result(tool_use_id, f"Error: {e}")
                        )
                elif command == "create":
                    file_text = tool_input.get("file_text", "")
                    try:
                        with open(path, "w") as f:
                            f.write(file_text)
                        tool_results.append(
                            build_tool_result(tool_use_id, f"Created {path}")
                        )
                    except Exception as e:
                        tool_results.append(
                            build_tool_result(tool_use_id, f"Error: {e}")
                        )
                elif command == "str_replace":
                    old_str = tool_input.get("old_str", "")
                    new_str = tool_input.get("new_str", "")
                    try:
                        with open(path, "r") as f:
                            content = f.read()
                        updated = content.replace(old_str, new_str, 1)
                        with open(path, "w") as f:
                            f.write(updated)
                        tool_results.append(
                            build_tool_result(tool_use_id, f"Replaced in {path}")
                        )
                    except Exception as e:
                        tool_results.append(
                            build_tool_result(tool_use_id, f"Error: {e}")
                        )
                else:
                    tool_results.append(
                        build_tool_result(tool_use_id, f"Unknown editor command: {command}")
                    )

        if not tool_results:
            print("  No tool actions to execute.")
            break

        messages.append({"role": "assistant", "content": content_blocks})
        messages.append({"role": "user", "content": tool_results})
        has_tool_results = True

        # Compress old turns to keep context window manageable
        messages = compress_context(messages)

    else:
        print(f"\nReached max steps ({max_steps}). Stopping.")
        print(f"Total tokens - input: {total_input_tokens}, output: {total_output_tokens}")

    print("\nDone.")


def main():
    parser = argparse.ArgumentParser(description="Bedrock Computer Use Agent v3.0")
    parser.add_argument("--task", required=True, help="Task description for the agent")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Bedrock model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--region", default=DEFAULT_REGION,
                        help=f"AWS region (default: {DEFAULT_REGION})")
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS,
                        help=f"Max loop iterations (default: {DEFAULT_MAX_STEPS})")
    parser.add_argument("--no-bash", action="store_true",
                        help="Disable bash tool (security: prevents shell command execution)")
    parser.add_argument("--no-editor", action="store_true",
                        help="Disable text editor tool (security: prevents file read/write)")
    args = parser.parse_args()

    run_computer_use(
        task=args.task,
        model_id=args.model,
        region=args.region,
        max_steps=args.max_steps,
        no_bash=args.no_bash,
        no_editor=args.no_editor,
    )


if __name__ == "__main__":
    main()
