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
import i3ipc

# A persistent connection object to be used by the application.
# This avoids the overhead of reconnecting for every check.
_connection = None

def get_sway_connection() -> i3ipc.Connection:
    """
    Establishes and returns a singleton connection to the Sway IPC.
    If the connection fails, it raises an exception.
    """
    global _connection
    if _connection is None:
        try:
            _connection = i3ipc.Connection()
        except Exception as e:
            print("Error: Could not connect to Sway IPC.")
            print(f"Please ensure Sway is running. Details: {e}")
            raise
    return _connection

def get_focused_window_title() -> str:
    """
    Connects to the Sway IPC and returns the title of the currently focused window.

    Returns:
        The window title as a string, or an empty string if no window is focused
        or an error occurs.
    """
    try:
        ipc = get_sway_connection()
        focused_window = ipc.get_tree().find_focused()

        if focused_window and focused_window.name:
            return focused_window.name
        else:
            # This can happen if a workspace is empty or a non-window
            # layer is focused (like a notification layer).
            return ""

    except Exception as e:
        print(f"Error when getting focused window title: {e}")
        # In case of an error (e.g., IPC disconnects), return a safe value.
        return ""

def close_sway_connection():
    """
    Closes the global Sway IPC connection if it's open.
    """
    global _connection
    if _connection:
        _connection.main_quit()
        _connection = None
        print("Sway IPC connection closed.")


if __name__ == "__main__":
    # This block allows for direct testing of the module.
    # To use: python -m src.sway_tracker
    print("Attempting to get focused window title...")
    try:
        title = get_focused_window_title()
        if title:
            print(f"Focused window: '{title}'")
        else:
            print("No focused window found or title is empty.")
    except Exception as e:
        print("Failed to get focused window title during test.")
    finally:
        # Important to clean up the connection when done.
        close_sway_connection()
