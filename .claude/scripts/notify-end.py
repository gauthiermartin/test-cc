#!/usr/bin/env python3
"""
Notification hook for ClaudeCode task completion
"""

import json
import subprocess
import sys
from pathlib import Path


def main():
    # Configuration
    SOUND_NAME = "Glass"

    # Read hook input data from standard input
    input_data = json.load(sys.stdin)

    # Get current session directory name (hooks run in the same directory as the session)
    session_dir = Path.cwd().name

    # Extract transcript_path
    transcript_path = input_data.get("transcript_path", "")

    # Default message
    msg = "Task completed"

    # If transcript_path exists, get the latest assistant message
    if transcript_path and Path(transcript_path).is_file():
        try:
            # Read the last 10 lines of the transcript
            with open(transcript_path, "r") as f:
                lines = f.readlines()
                last_lines = lines[-10:] if len(lines) >= 10 else lines

            # Parse and extract assistant messages
            assistant_msg = None
            for line in last_lines:
                try:
                    entry = json.loads(line)
                    if entry.get("message", {}).get("role") == "assistant":
                        content = entry.get("message", {}).get("content", [])
                        if content and isinstance(content, list) and len(content) > 0:
                            text = content[0].get("text", "")
                            if text:
                                assistant_msg = text
                except json.JSONDecodeError:
                    continue

            if assistant_msg:
                # Remove newlines and limit to 60 characters
                msg = assistant_msg.replace("\n", " ")[:60]

        except (IOError, OSError):
            pass  # Use default message

    # Display macOS notification with sound using osascript
    notification_title = f"ClaudeCode ({session_dir}) Task Done"

    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{msg}" with title "{notification_title}"',
        ]
    )

    # Play sound
    sound_path = f"/System/Library/Sounds/{SOUND_NAME}.aiff"
    subprocess.run(["afplay", sound_path])


if __name__ == "__main__":
    main()
