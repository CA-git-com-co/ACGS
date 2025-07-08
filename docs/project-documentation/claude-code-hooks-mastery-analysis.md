<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# Claude Code Hooks Mastery - Analysis & Reusable Snippets

## Repository Overview

**Repository:** https://github.com/disler/claude-code-hooks-mastery
**Purpose:** Demonstrates Claude Code hooks using UV single-file scripts for deterministic control over Claude Code behavior
**Architecture:** UV single-file scripts with embedded dependencies for hook lifecycle management

## UV Single-File Script Conventions

### 1. Standard Shebang Pattern
```python
#!/usr/bin/env -S uv run --script
```
**Key Features:**
- Uses `-S` flag to split arguments properly
- Enables `uv run --script` for dependency management
- Self-contained execution without virtual environments

### 2. Script Metadata Block
```python
# /// script
# requires-python = ">=3.8"  # or ">=3.11" for newer features
# dependencies = [
#     "package-name",
#     "another-package>=1.0.0",
# ]
# ///
```

**Dependency Examples Found:**
- **Basic Scripts:** No dependencies (pre_tool_use.py, post_tool_use.py)
- **Enhanced Scripts:** `["python-dotenv"]` for environment variable management
- **TTS Scripts:** `["elevenlabs"]`, `["pyttsx3"]` for audio
- **LLM Scripts:** `["openai"]`, `["anthropic"]` for AI services

### 3. Import Pattern with Graceful Degradation
```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional
```

## Claude Code Hook Lifecycle Events

### 1. PreToolUse Hook
**Fires:** Before any tool execution
**Capabilities:** Can block tool execution
**JSON Input:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../conversation.jsonl",
  "tool_name": "Write|Edit|Bash|Read|etc",
  "tool_input": {
    "file_path": "/path/to/file",
    "command": "bash command",
    "content": "file content"
  }
}
```

**Exit Code Behaviors:**
- `0`: Success, continue execution
- `2`: Block tool call, show stderr to Claude
- Other: Non-blocking error

### 2. PostToolUse Hook
**Fires:** After successful tool completion
**Capabilities:** Cannot block (tool already executed)
**JSON Input:** Same as PreToolUse + `tool_response` field

### 3. Notification Hook
**Fires:** When Claude Code sends notifications
**Capabilities:** Cannot block, informational only
**JSON Input:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../conversation.jsonl",
  "message": "Notification message",
  "title": "Claude Code"
}
```

### 4. Stop Hook
**Fires:** When Claude Code finishes responding
**Capabilities:** Can block stopping, force continuation
**JSON Input:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../conversation.jsonl",
  "stop_hook_active": true
}
```

### 5. SubagentStop Hook
**Fires:** When Claude Code subagents finish
**Capabilities:** Can block subagent stopping
**JSON Input:** Same as Stop Hook

## Reusable Code Snippets

### 1. Standard Hook Template
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "python-dotenv",  # Optional for environment variables
# ]
# ///

import json
import os
import sys
from pathlib import Path

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Extract common fields
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        session_id = input_data.get('session_id', '')

        # Your hook logic here

        # Logging pattern
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'hook_name.json'

        # Read existing log data
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)  # Graceful failure
    except Exception:
        sys.exit(0)  # Graceful failure

if __name__ == '__main__':
    main()
```

### 2. Security Validation Pattern (PreToolUse)
```python
def is_dangerous_rm_command(command):
    """Comprehensive detection of dangerous rm commands."""
    normalized = ' '.join(command.lower().split())

    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',  # rm -rf variations
        r'\brm\s+.*-[a-z]*f[a-z]*r',  # rm -fr variations
        r'\brm\s+--recursive\s+--force',
        r'\brm\s+--force\s+--recursive',
    ]

    for pattern in patterns:
        if re.search(pattern, normalized):
            return True
    return False

def is_env_file_access(tool_name, tool_input):
    """Check if accessing sensitive .env files."""
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
        file_path = tool_input.get('file_path', '')
        if '.env' in file_path and not file_path.endswith('.env.sample'):
            return True

    if tool_name == 'Bash':
        command = tool_input.get('command', '')
        env_patterns = [
            r'\b\.env\b(?!\.sample)',  # .env but not .env.sample
            r'cat\s+.*\.env\b(?!\.sample)',
        ]
        for pattern in env_patterns:
            if re.search(pattern, command):
                return True
    return False

# Usage in hook:
if is_dangerous_rm_command(command):
    print("BLOCKED: Dangerous rm command detected", file=sys.stderr)
    sys.exit(2)  # Block tool execution
```

### 3. TTS Service Priority Pattern
```python
def get_tts_script_path():
    """
    Determine TTS script based on available API keys.
    Priority: ElevenLabs > OpenAI > pyttsx3
    """
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"

    # Check ElevenLabs (highest priority)
    if os.getenv('ELEVENLABS_API_KEY'):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check OpenAI (second priority)
    if os.getenv('OPENAI_API_KEY'):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None

def announce_with_tts(message):
    """Announce message via best available TTS."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return

        subprocess.run([
            "uv", "run", tts_script, message
        ],
        capture_output=True,
        timeout=10
        )
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass  # Fail silently
```

### 4. LLM Service Integration Pattern
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "openai",  # or "anthropic"
#     "python-dotenv",
# ]
# ///

def prompt_llm(prompt_text):
    """Base LLM prompting with error handling."""
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")  # or ANTHROPIC_API_KEY
    if not api_key:
        return None

    try:
        from openai import OpenAI  # or import anthropic

        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # or claude-3-5-haiku-20241022
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=100,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return None

def generate_completion_message():
    """Generate context-aware completion message."""
    engineer_name = os.getenv("ENGINEER_NAME", "").strip()

    prompt = f"""Generate a short, friendly completion message.
    Requirements:
    - Under 10 words
    - Positive and future focused
    - Natural, conversational language
    {"- Sometimes include name: " + engineer_name if engineer_name else ""}

    Generate ONE completion message:"""

    response = prompt_llm(prompt)
    if response:
        response = response.strip().strip('"').strip("'").strip()
        response = response.split("\n")[0].strip()

    return response or "Work complete!"
```

### 5. Command Line Argument Pattern
```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--notify', action='store_true', help='Enable TTS notifications')
    parser.add_argument('--chat', action='store_true', help='Copy transcript to chat.json')
    args = parser.parse_args()

    # Use flags in logic
    if args.notify:
        announce_notification()

    if args.chat and 'transcript_path' in input_data:
        convert_transcript_to_json(input_data['transcript_path'])
```

### 6. Transcript Processing Pattern
```python
def convert_transcript_to_json(transcript_path):
    """Convert JSONL transcript to readable JSON array."""
    if not os.path.exists(transcript_path):
        return

    chat_data = []
    try:
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        chat_data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass  # Skip invalid lines

        # Write to logs/chat.json
        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        chat_file = log_dir / 'chat.json'

        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
    except Exception:
        pass  # Fail silently
```

## Hook Configuration Patterns

### settings.json Structure
```json
{
  "permissions": {
    "allow": [
      "Bash(mkdir:*)",
      "Bash(uv:*)",
      "Write",
      "Edit"
    ],
    "deny": []
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "",  // Empty = all tools, or "Bash|Write" for specific
        "hooks": [
          {
            "type": "command",
            "command": "uv run .claude/hooks/pre_tool_use.py"
          }
        ]
      }
    ],
    "PostToolUse": [...],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run .claude/hooks/notification.py --notify"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "uv run .claude/hooks/stop.py --chat"
          }
        ]
      }
    ]
  }
}
```

## Project Structure Convention
```
.claude/
├── settings.json           # Hook configuration
└── hooks/                  # UV single-file scripts
    ├── pre_tool_use.py    # Security & validation
    ├── post_tool_use.py   # Logging & cleanup
    ├── notification.py    # User alerts
    ├── stop.py            # Completion handling
    ├── subagent_stop.py   # Subagent completion
    └── utils/             # Shared utilities
        ├── tts/           # Text-to-speech services
        │   ├── elevenlabs_tts.py
        │   ├── openai_tts.py
        │   └── pyttsx3_tts.py
        └── llm/           # Language model services
            ├── oai.py     # OpenAI integration
            └── anth.py    # Anthropic integration

logs/                       # Generated by hooks
├── pre_tool_use.json      # Security events
├── post_tool_use.json     # Tool completion events
├── notification.json      # Notification events
├── stop.json              # Stop events
├── subagent_stop.json     # Subagent events
└── chat.json              # Readable conversation transcript
```

## Key Benefits of This Architecture

1. **Isolation:** Hook logic separated from main codebase dependencies
2. **Portability:** Each script declares its own dependencies inline
3. **No Virtual Environment Management:** UV handles dependencies automatically
4. **Fast Execution:** UV's dependency resolution is lightning-fast
5. **Self-Contained:** Each hook can be understood and modified independently
6. **Graceful Degradation:** Scripts handle missing dependencies and API keys elegantly
7. **Deterministic Control:** Hooks provide guaranteed behavior vs LLM decisions

## Environment Variables Used

- `ELEVENLABS_API_KEY`: ElevenLabs TTS service
- `OPENAI_API_KEY`: OpenAI LLM and TTS services
- `ANTHROPIC_API_KEY`: Anthropic Claude LLM service
- `ENGINEER_NAME`: Personalization for TTS messages

## Advanced JSON Output Control

Hooks can return structured JSON for sophisticated control:

```python
# Block tool execution with reason
output = {
    "decision": "block",
    "reason": "File write operation failed, please check permissions"
}
print(json.dumps(output))
sys.exit(0)

# Continue with suppressed output
output = {
    "continue": true,
    "suppressOutput": true
}
print(json.dumps(output))
sys.exit(0)
```

This architecture enables production-ready Claude Code customization with maintainable, isolated hook scripts that leverage UV's excellent dependency management capabilities.
