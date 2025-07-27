# This file is part of time-narrator.
#
# time-narrator is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# time-narrator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with time-narrator.  If not, see <https://www.gnu.org/licenses/>.

"""
Time Narrator: A tool to narrate time and activity.
"""
import argparse
import random
import subprocess
import sys
import time
from collections import Counter

from .config import APP_CONFIG, write_default_config
from .idle_tracker import IdleTracker
from .sway_tracker import close_sway_connection, get_focused_window_title


def narrate(text: str):
    """
    Uses the configured TTS command to speak the given text by piping it to the command's stdin.
    """
    try:
        # Use shell=True to allow for command pipelines (e.g., piper | aplay).
        # The text to be spoken is passed to the command's standard input.
        subprocess.run(
            APP_CONFIG.tts_command,
            input=text,
            shell=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error executing TTS command: '{APP_CONFIG.tts_command}'")
        print(f"Return code: {e.returncode}")

    except Exception as e:
        # Catch any other unexpected errors during subprocess execution
        print(f"An unexpected error occurred while trying to narrate: {e}")


def main():
    """
    Time Narrator: A background service that periodically tells you the time and what you've been working on.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "--write-default-config",
        action="store_true",
        help="Write the default config to ~/.config/time-narrator/config.toml and exit.",
    )
    parser.add_argument(
        "--tts-command",
        type=str,
        default=None,
        help="Override the TTS command from the configuration file.",
    )
    args = parser.parse_args()

    if args.write_default_config:
        print("Writing default configuration file...")
        write_default_config()
        sys.exit(0)

    if args.tts_command:
        APP_CONFIG.tts_command = args.tts_command

    print("Time Narrator starting up...")
    print(f"Loaded configuration: {APP_CONFIG}")

    idle_tracker = IdleTracker(idle_threshold_sec=APP_CONFIG.idle_threshold_sec)
    idle_tracker.start()

    # Give the idle tracker a moment to initialize and check if it's running
    time.sleep(1)
    if not idle_tracker.is_alive():
        print(
            "Error: Idle tracker thread failed to start. "
            "This may be because the compositor does not support the idle protocol. Exiting."
        )
        sys.exit(1)

    # How often we check the user's state, in seconds.
    TICK_INTERVAL_SEC = 2
    activity_log = []
    idle_tick_counter = 0
    last_reminder_time = None  # The time the last reminder was given.

    def schedule_next_reminder() -> float:
        """Calculates the absolute timestamp for the next reminder."""
        delay = APP_CONFIG.base_interval_sec + random.randint(
            -APP_CONFIG.random_window_sec, APP_CONFIG.random_window_sec
        )
        print(f"INFO: Next reminder in {delay // 60} minutes and {delay % 60} seconds.")
        return time.time() + delay

    next_reminder_time = 0  # Set to 0 to trigger the first reminder immediately.
    last_narration_time = 0.0

    try:
        while True:
            time.sleep(TICK_INTERVAL_SEC)

            # 1. Track activity or idle state
            if idle_tracker.is_user_idle():
                idle_tick_counter += 1
            else:
                title = get_focused_window_title()
                if title:  # Only log if there is a window title
                    activity_log.append(title)

            # 2. Check if it's time for a reminder
            if time.time() >= next_reminder_time:
                time_now = time.time()

                # Announce the time first
                current_time_str = time.strftime("%I:%M %p")
                narrate(f"The time is {current_time_str}.")
                time.sleep(0.2)  # Small pause for clarity

                # Determine the most significant activity since the last reminder
                total_active_ticks = len(activity_log)
                total_idle_ticks = idle_tick_counter

                activity_summary = ""
                if total_active_ticks > total_idle_ticks:
                    if activity_log:
                        # Find the most frequent window title
                        most_common_activity = Counter(activity_log).most_common(1)[0][0]
                        print(f"INFO: Most common activity: '{most_common_activity}'")
                        activity_summary = f"you were doing {most_common_activity}."
                else:
                    # User was mostly idle
                    print("INFO: User was mostly idle.")
                    activity_summary = "you weren't at your computer."

                # Build the narration for the activity summary
                if activity_summary:
                    duration_message = ""
                    # For subsequent reminders, describe the duration.
                    if last_reminder_time:
                        duration_sec = time_now - last_reminder_time
                        if duration_sec > 60:
                            duration_min = round(duration_sec / 60)
                            if duration_min == 1:
                                duration_message = "In the past minute, "
                            else:
                                duration_message = f"In the past {duration_min} minutes, "

                    narrate(f"{duration_message}{activity_summary}")

                # 3. Reset state for the next interval
                activity_log.clear()
                idle_tick_counter = 0
                last_reminder_time = time_now
                next_reminder_time = schedule_next_reminder()

    except KeyboardInterrupt:
        print("\nCaught interrupt signal. Shutting down...")
    finally:
        print("Cleaning up resources...")
        idle_tracker.stop()
        idle_tracker.join()
        close_sway_connection()
        print("Cleanup complete. Goodbye.")


if __name__ == "__main__":
    main()
