import threading
import time
import subprocess


class IdleTracker(threading.Thread):
    def __init__(self, idle_threshold_sec: int):
        super().__init__()
        self.idle_threshold_sec = idle_threshold_sec
        self._is_idle = False
        self._process = None
        self._stop_event = threading.Event()
        self.daemon = True

    def is_user_idle(self) -> bool:
        return self._is_idle

    def stop(self):
        self._stop_event.set()
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._process.kill()

    def run(self):
        """
        Runs swayidle in a subprocess and monitors its stdout for idle/resume events.
        """
        command = [
            "swayidle",
            "-w",
            "timeout",
            str(self.idle_threshold_sec),
            "echo idle",
            "resume",
            "echo resume",
        ]

        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        except FileNotFoundError:
            print("Error: 'swayidle' command not found. Please install it and ensure it's in your PATH.")
            return

        if self._process.stdout:
            # Read from stdout line by line until the process terminates
            for line in iter(self._process.stdout.readline, ''):
                if self._stop_event.is_set():
                    break
                output = line.strip()
                if output == "idle":
                    self._is_idle = True
                elif output == "resume":
                    self._is_idle = False
            self._process.stdout.close()

        # Cleanly wait for the process to exit and check for errors
        return_code = self._process.wait()
        if return_code != 0 and not self._stop_event.is_set():
            stderr_output = self._process.stderr.read()
            print(f"swayidle exited unexpectedly with code {return_code}.")
            if stderr_output:
                print(f"Stderr: {stderr_output.strip()}")

        if self._process.stderr:
            self._process.stderr.close()
