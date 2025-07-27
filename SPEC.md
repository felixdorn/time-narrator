# Project Specification: "Time Narrator"

## 1. Overview

**Time Narrator** is a background utility for Sway compositor on Linux that helps users maintain awareness of time and their computer usage. It periodically announces the current time, followed by a summary of the user's most significant activity or idle state since the last announcement.

The goal is to provide a gentle, ambient reminder of the passage of time and the focus of one's attention without being intrusive or requiring manual interaction.

## 2. Core Functionality

### 2.1. Activity Tracking

*   **Mechanism**: The application will track user activity by monitoring the currently focused window in Sway.
*   **Data Source**: Activity will be logged by periodically sampling the title of the focused window. The application that the user spent the most time in will be determined by which window title was active for the longest duration between two reminders.
*   **Granularity**: The full window title (e.g., `"Project Specification: 'Time Narrator' - Google Docs - Firefox"`) will be used as the identifier for the activity. No further processing or classification of the title will be performed.

### 2.2. Idle Detection

*   **Mechanism**: The application will natively implement the `ext-idle-notify-v1` Wayland protocol to monitor user idle status. This allows for efficient, event-driven idle detection.
*   **Behavior**:
    1.  Upon startup, the application will connect to the Wayland compositor and request an idle notification object, configured with the `idle_threshold_sec` from the user's settings.
    2.  When the compositor sends an `idled` event, the application will pause tracking window titles and will start accumulating time in an "idle" state.
    3.  When the compositor sends a `resumed` event, the application will stop counting idle time and resume tracking the active window title.
*   **Protocol Choice**: The application should use the `get_input_idle_notification` request if available. This ensures that it tracks physical user presence (keyboard/mouse) and is not fooled by applications that inhibit idleness (like video players).

### 2.3. Reminder Scheduling

*   **Frequency**: Reminders will be triggered approximately 3 times per hour.
*   **Logic**: The scheduling will have a degree of randomness to feel more natural. After a reminder is sent, the next reminder will be scheduled to occur after a `base_interval` plus or minus a `random_window`.
    *   *Example*: With a `base_interval` of 20 minutes and a `random_window` of 5 minutes, the next reminder will fire at a random point between 15 and 25 minutes from the last one.

### 2.4. Notification (TTS Output)

*   **Engine**: The user will specify a command-line Text-to-Speech (TTS) engine. The application will execute this command to produce the audio output.
    *   **Requirement**: The chosen TTS engine must be able to run offline.
    *   **Recommendation**: `piper` is a high-quality, modern offline TTS engine. `espeak-ng` is a simpler, more robotic-sounding but universally available alternative. The choice is left to the user.
*   **Message Format**: The announcement will have two parts: the time, and the context.

    1.  **Time Announcement**: `"The time is {hour}:{minute} {AM/PM}."`
    2.  **Context Announcement**: This will be one of the following:
        *   **If activity was tracked**: `"You were doing {window_title}."`
        *   **If the majority of the time was spent idle**: `"You weren't at your computer."`

## 3. Technical Implementation

*   **Architecture**: The application will be a long-running background process (daemon). It will maintain its state in memory between reminders.
*   **Language/Platform**: This will be implemented in Python. It has mature libraries for handling Wayland protocols (`pywayland`) and system services, which aligns perfectly with our requirements.
*   **Dependencies**:
    *   A running Sway compositor that supports the `ext-idle-notify-v1` protocol.
    *   A Sway IPC library to get the focused window (e.g., `i3ipc-python`).
    *   A Wayland client library that can handle the `ext-idle-notify-v1` protocol (e.g., `pywayland`).
    *   A command-line TTS application installed on the system.
*   **Deployment**: The application will be packaged with a `systemd` user service file for easy setup. The user can enable it to start automatically on login with `systemctl --user enable --now time-narrator.service`.

## 4. Configuration

The application will be configured via a file located at `~/.config/time-narrator/config.toml`.

### 4.1. Example `config.toml`

```toml
# Command to execute for text-to-speech. Must accept a string as the last argument.
# Example for piper (sending output to aplay):
# tts_command = "piper --model en_US-lessac-medium.onnx --output_file - | aplay -r 22050 -f S16_LE -t raw -"
# Example for espeak-ng:
tts_command = "espeak-ng"

# The base interval for reminders, in seconds.
base_interval_sec = 1200 # 20 minutes

# The random window to add or subtract from the base interval, in seconds.
# A value of 300 means the reminder can be +/- 5 minutes from the base interval.
random_window_sec = 300 # 5 minutes

# The number of seconds of inactivity after which the user is considered "idle".
idle_threshold_sec = 60
```
