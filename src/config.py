import dataclasses
import os
import tomllib
from pathlib import Path

@dataclasses.dataclass(frozen=True)
class Config:
    """
    Holds the application configuration.
    Using a frozen dataclass makes the configuration immutable, which is a good practice.
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
    # Start with the default configuration values
    config_values = {
        "tts_command": "espeak-ng",
        "base_interval_sec": 600,
        "random_window_sec": 300,
        "idle_threshold_sec": 60,
    }

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

tts_command = "{APP_CONFIG.tts_command}"

# Reminder interval in seconds (e.g., 20 minutes)
base_interval_sec = {APP_CONFIG.base_interval_sec}

# Randomness window in seconds (e.g., +/- 5 minutes)
random_window_sec = {APP_CONFIG.random_window_sec}

# Seconds of inactivity to be considered "idle"
idle_threshold_sec = {APP_CONFIG.idle_threshold_sec}
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
