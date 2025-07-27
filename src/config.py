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

import dataclasses
import os
import tomllib
from pathlib import Path

# The default configuration values, used as a fallback.
DEFAULT_CONFIG_VALUES = {
    "tts_command": "espeak-ng",
    "base_interval_sec": 600,
    "random_window_sec": 300,
    "idle_threshold_sec": 60,
}


@dataclasses.dataclass
class Config:
    """
    Holds the application configuration.
    This object is mutable, allowing its values to be updated during runtime.
    """
    tts_command: str
    base_interval_sec: int
    random_window_sec: int
    idle_threshold_sec: int


def _get_config_path() -> Path:
    """
    Gets the path to the user's configuration file, following XDG standards.
    The path is ~/.config/time-narrator/config.toml.
    """
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        # If XDG_CONFIG_HOME is set, use it
        return Path(config_home) / "time-narrator" / "config.toml"

    # Otherwise, default to ~/.config
    return Path.home() / ".config" / "time-narrator" / "config.toml"


def load_config() -> Config:
    """
    Loads configuration by reading the user's config file and merging it
    with default values.

    If the config file is not found or is invalid, defaults will be used.
    """
    # Start with a copy of the default configuration values
    config_values = DEFAULT_CONFIG_VALUES.copy()

    config_path = _get_config_path()

    if config_path.is_file():
        try:
            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)

            # Update the defaults with any values the user has provided
            config_values.update(user_config)
            print(f"Loaded configuration from: {config_path}")

        except tomllib.TOMLDecodeError as e:
            print(f"Error: Could not parse config file at {config_path}. Invalid TOML.")
            print(f"Details: {e}")
            print("Using default configuration.")
        except (IOError, OSError) as e:
            print(f"Error: Could not read config file at {config_path}.")
            print(f"Details: {e}")
            print("Using default configuration.")
    else:
        print("No config file found. Using default configuration.")

    return Config(**config_values)


def write_default_config():
    """
    Writes the default configuration to the user's config file path.
    This is useful for allowing users to easily create a new config file.
    """
    config_path = _get_config_path()
    config_dir = config_path.parent

    # Create the config directory if it doesn't exist
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except (IOError, OSError) as e:
        print(f"Error: Could not create config directory at {config_dir}.")
        print(f"Details: {e}")
        return

    default_config_toml = f"""# The command to execute for text-to-speech.
# This example uses a shell pipe, which is supported.
# tts_command = "bash -c 'piper --model /path/to/model.onnx --output-file - | pw-play -'"

tts_command = "{DEFAULT_CONFIG_VALUES['tts_command']}"

# Reminder interval in seconds (e.g., 20 minutes)
base_interval_sec = {DEFAULT_CONFIG_VALUES['base_interval_sec']}

# Randomness window in seconds (e.g., +/- 5 minutes)
random_window_sec = {DEFAULT_CONFIG_VALUES['random_window_sec']}

# Seconds of inactivity to be considered "idle"
idle_threshold_sec = {DEFAULT_CONFIG_VALUES['idle_threshold_sec']}
"""

    try:
        with open(config_path, "w") as f:
            f.write(default_config_toml)
        print(f"Default configuration written to: {config_path}")
    except (IOError, OSError) as e:
        print(f"Error: Could not write to config file at {config_path}.")
        print(f"Details: {e}")


# Create a single, project-wide instance of the configuration.
# Other modules can import this instance directly.
APP_CONFIG = load_config()
