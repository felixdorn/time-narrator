# Time Narrator

Time Narrator is a background service for the Sway window manager that periodically tells you the time and summarizes your recent activity. It's a tool designed to foster time awareness and mindful computing without interrupting your workflow.

## The Benefit of Audible Feedback

In the age of deep work and digital immersion, it's easy to lose track of time. You might sit down to work on a small task, only to find that hours have passed by unnoticed. Time Narrator aims to solve this by providing gentle, ambient, and audible feedback.

-   **Maintain Time Awareness:** By narrating the time at semi-random intervals, the tool helps you build a better internal clock. This can improve time management and prevent you from spending unintended amounts of time on a single task.
-   **Promote Mindful Computing:** The activity summary encourages a moment of reflection. Hearing "In the past 20 minutes, you were working on Project X" reinforces that you're on track, while hearing "you weren't at your computer" can be a useful reminder of your breaks. It provides a low-friction form of accountability.
-   **Reduce Distractions:** Unlike visual notifications, audible alerts don't require you to shift your visual focus. You can continue typing, reading, or designing while the narrator speaks, keeping you in your flow state.

## Prerequisites

Before installing, you need to have the following installed on your system:

-   **Sway** and **`swayidle`**: The tool is built specifically for the Sway environment.
-   **TTS Engine**: `espeak-ng` or `piper` or other.. You pick the comand.

## Installation
```bash
uvx time-narrator
```

## Configuration
  ```bash
uv run time-narrator --write-default-config
```

This will create a new file at `~/.config/time-narrator/config.toml`.

### Options
- `tts_command`: The shell command used to speak text. The script pipes the narration text to this command's standard input.
  - Example #1: `tts_command = "espeak-ng"`
  - Example #2 (higher quality): `tts_command = "piper --model /path/to/en_US-lessac-medium.onnx --output-file - | pw-play"`
- `base_interval_sec`: The base interval for reminders, in seconds. (Default: `600`, i.e., 10 minutes).
- `random_window_sec`: A window to add or subtract from the base interval, in seconds. (Default: `300`, i.e., +/- 5 minutes). This means reminders will occur every 5 to 15 minutes.
- `idle_threshold_sec`: The number of seconds of inactivity before you are considered "idle". (Default: `60`).

## Usage

**Launching from sway config**

```
exec time-narrator
```
