---
name: computer-use
description: |
  Amazon Bedrock Computer Use - Desktop GUI automation agent.
  Use this skill whenever the user wants to control their computer screen,
  automate GUI interactions, click buttons, fill forms, navigate applications,
  or perform any desktop automation task. Trigger phrases include:
  "computer use", "screen control", "GUI automation", "click on screen",
  "automate GUI", "browser automation", "mouse click", "desktop automation",
  "open app and do X", "navigate to", "fill in the form", "take a screenshot
  and interact". This skill drives real mouse/keyboard via pyautogui based on
  model analysis of screenshots through the Bedrock Converse API agentic loop.
  Use it any time the user wants something done visually on their desktop.
license: MIT License
metadata:
  skill-author: jesamkim
  version: 3.0.0
allowed-tools: [Bash, Read, Write, Glob]
---

# computer-use - Bedrock Computer Use GUI Automation

## Overview

An agentic desktop GUI automation tool powered by Amazon Bedrock Converse API's Computer Use capability.
The model analyzes screenshots, issues mouse/keyboard/scroll actions, and pyautogui executes them
in a continuous loop until the task is complete.

**v3.0 key improvements:**
- Pre-planning: system prompt guides model to plan subtasks and batch multiple actions per turn
- Batch execution: only the last computer action in a turn captures a verification screenshot, reducing redundant vision calls
- Context compression: old turn screenshots are replaced with text placeholders, keeping the context window lean even on long tasks
- Model version auto-detection (supports Claude 3.5 through 4.6)
- Intelligent retry with exponential backoff for transient API errors
- Token usage tracking and reporting

**Default model**: `global.anthropic.claude-opus-4-6-v1` (Opus 4.6, Cross-Region)

**API**: Bedrock Converse API + `additionalModelRequestFields`

## Supported Models & Tool Version Matrix

The script auto-detects the correct tool versions and beta headers based on model ID.

| Generation | Models | Computer Tool | Beta Header |
|------------|--------|--------------|-------------|
| **4.6** | Opus 4.6, Sonnet 4.6 | `computer_20251124` | `computer-use-2025-11-24` |
| **4.5** | Opus 4.5, Sonnet 4.5, Haiku 4.5 | `computer_20250124` | `computer-use-2025-01-24` |
| **4.x** | Opus 4.1, Sonnet 4.0 | `computer_20250124` | `computer-use-2025-01-24` |
| **3.5** | Claude 3.5 Sonnet v2 | `computer_20241022` | `computer-use-2024-10-22` |

> **Note**: Opus 4.5 uses `text_editor_20250728` + `str_replace_based_edit_tool`. Other 4.5/4.x models use `text_editor_20250124` + `str_replace_editor`.

### Recommended model by use case

| Use Case | Recommended Model | Reason |
|----------|------------------|--------|
| Complex GUI tasks | Opus 4.6 (default) | Best recovery behavior, highest accuracy |
| Standard automation | Sonnet 4.5 / 4.6 | Good balance of cost and capability |
| Simple verification | Haiku 4.5 | Fastest, cheapest, 50.7% OSWorld score |

## Prerequisites

On macOS, the following permissions are required:
- **Accessibility**: System Settings > Privacy & Security > Accessibility — grant permission to the terminal app
- **Screen Recording**: System Settings > Privacy & Security > Screen Recording — required for screenshot capture

Python dependencies are automatically installed via venv in Step 1.

## Workflow

### Step 1: Prepare venv (automatic)

Before running the script, check for `.venv` in this skill directory. Create it if missing, otherwise just activate:

```bash
SKILL_DIR="<skill-path>"
VENV_DIR="${SKILL_DIR}/.venv"

if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating venv at ${VENV_DIR}..."
  python3 -m venv "${VENV_DIR}"
  source "${VENV_DIR}/bin/activate"
  pip install -r "${SKILL_DIR}/requirements.txt"
else
  source "${VENV_DIR}/bin/activate"
fi
```

> Replace `<skill-path>` with the absolute path of the directory containing this SKILL.md.

### Step 2: Ask the user for max steps (required)

Before running the script, **always** ask the user how many steps to allow.
The default is 50. If the user specifies a number, pass it to `--max-steps`.

Example prompt:
> "How many max steps should I allow? (default: 50)"

If the user says to just proceed without specifying, use the default of 50.

### Step 3: Analyze user request

Identify the GUI task the user wants to automate.

| Request type | Example |
|-------------|---------|
| Web browser | "Go to the S3 bucket list in the AWS Console" |
| Application | "Open the Downloads folder in Finder" |
| Form input | "Enter my email on the login page" |
| Repetitive | "Click this button 5 times" |

### Step 4: Run the script

After activating the venv from Step 1, run `scripts/computer_use.py`.
Use the max-steps value from Step 2. Always chain venv activation and script execution in a single command:

```bash
source <skill-path>/.venv/bin/activate && python <skill-path>/scripts/computer_use.py --task "task description"
```

**Examples:**

```bash
# Default (Opus 4.6)
source <skill-path>/.venv/bin/activate && \
  python <skill-path>/scripts/computer_use.py --task "Navigate to the Bedrock service page in AWS Console"

# Specify model (e.g., Sonnet 4.5 for cost savings)
source <skill-path>/.venv/bin/activate && \
  python <skill-path>/scripts/computer_use.py \
  --task "Search in the browser" \
  --model us.anthropic.claude-sonnet-4-5-20250929-v1:0

# Custom max steps
source <skill-path>/.venv/bin/activate && \
  python <skill-path>/scripts/computer_use.py \
  --task "Enable dark mode in settings" \
  --max-steps 30

# Specify region
source <skill-path>/.venv/bin/activate && \
  python <skill-path>/scripts/computer_use.py \
  --task "Perform task" \
  --region us-east-1
```

### Step 5: Agentic loop mechanics

The script repeats the following loop with built-in reliability features:

```
1. Capture screenshot (macOS screencapture)
     |
2. Call Bedrock Converse API (with retry on transient errors)
   - System prompt guides model reasoning
   - Screenshot + task description sent
   - Tool versions auto-matched to model
     |
3. Parse model response
   - stop_reason == "end_turn" -> done, exit loop
   - stop_reason == "tool_use" -> action needed
     |
4. Execute action (pyautogui)
   - screenshot, left_click, right_click, double_click, triple_click
   - mouse_move, left_click_drag, left_mouse_down, left_mouse_up
   - type, key, hold_key
   - scroll, scroll_up, scroll_down
   - wait
     |
5. Verification: capture screenshot after action to confirm result
     |
6. Append tool_result to messages and return to step 2
```

### Step 6: Review results

The script logs each step to the console:
- Model reasoning at each step
- Which action was executed with coordinates
- Token usage per step and cumulative total
- Retry attempts for transient errors
- Final completion message with total token count

## Retry Behavior

Transient errors are automatically retried with exponential backoff:
- **Retryable**: ThrottlingException, 429, 5xx, connection/timeout errors
- **Non-retryable**: 4xx validation errors, invalid model ID, auth failures
- **Max retries**: 3 with exponential backoff + jitter
- **Backoff**: 1s, 2s, 4s (+ random 0-1s jitter)

## Security Considerations

Computer Use controls the actual desktop, so exercise caution:

- **`--no-bash`**: Disables the bash tool — prevents the model from executing shell commands
- **`--no-editor`**: Disables the text editor tool — prevents the model from reading/writing files
- Avoid running while sensitive accounts are logged in
- Prefer running in a dedicated VM or Docker container when possible
- The script adds a 0.5-second delay before each action so you can press Ctrl+C to abort
- Use `--max-steps` to limit the maximum number of iterations (default: 50)
- pyautogui FAILSAFE is enabled — move mouse to screen corner to abort
- `hold_key` capped at 10s, `wait` capped at 30s to prevent indefinite blocking

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `pyautogui.FailSafeException` | Moving the mouse to a screen corner triggers the failsafe. This is expected behavior |
| Accessibility permission error | Grant permission in System Settings > Privacy & Security > Accessibility |
| Screenshot is black screen | Check Screen Recording permission |
| `ValidationException` | Check model ID matches a supported model — tool versions are auto-detected |
| Coordinates are misaligned | Retina display scaling issue — the script handles this automatically |
| `ThrottlingException` | Automatic retry with backoff; if persistent, check Bedrock quotas |
| Wrong tool version error | The script auto-detects; if a new model is released, update `detect_model_config()` |
