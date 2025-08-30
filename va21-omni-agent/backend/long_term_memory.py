import os
import json
import secrets
from datetime import datetime, timedelta

class LongTermMemoryManager:
    def __init__(self, data_dir="data"):
        self.memory_file = os.path.join(data_dir, "ltm.json")
        self.memory = self._load_memory()

    def _load_memory(self):
        """Loads the long-term memory from a JSON file."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        else:
            # First launch: generate dev mode code and create the file
            dev_code = secrets.token_hex(16)
            initial_memory = {
                "dev_mode_code": dev_code
            }
            # Ensure the data directory exists
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(initial_memory, f, indent=2)
            return initial_memory

    def _save_memory(self):
        """Saves the long-term memory to a JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def remember(self, key, value):
        """Saves a key-value pair to long-term memory."""
        self.memory[key] = value
        self._save_memory()
        return f"I will remember that {key} is {value}."

    def recall(self, key):
        """Recalls a value from long-term memory."""
        value = self.memory.get(key)
        if value:
            return f"I recall that {key} is {value}."
        else:
            return f"I don't have any memory of '{key}'."

    def get_all(self):
        """Returns the entire long-term memory."""
        return self.memory

    def set_observation_mode(self, days=5):
        """Sets the agent to be in observation mode for a number of days."""
        end_time = datetime.now() + timedelta(days=days)
        self.remember("observation_mode_until", end_time.isoformat())
        print(f"[OBSERVATION MODE] Activated until {end_time.isoformat()}")

    def is_in_observation_mode(self):
        """Checks if the agent is currently in observation mode."""
        end_time_str = self.memory.get("observation_mode_until")
        if not end_time_str:
            return False

        try:
            end_time = datetime.fromisoformat(end_time_str)
            if datetime.now() < end_time:
                return True
            else:
                # The observation period has expired, so clear the flag.
                self.remember("observation_mode_until", None)
                return False
        except ValueError:
            # Handle cases where the timestamp is invalid.
            return False

    def set_lockdown_mode(self, enable: bool):
        """
        Enables or disables lockdown mode.
        This is a persistent state until explicitly disabled.
        """
        self.remember("lockdown_mode_active", enable)
        if enable:
            print("[LOCKDOWN MODE] Activated.")
        else:
            print("[LOCKDOWN MODE] Deactivated.")

    def is_in_lockdown_mode(self):
        """Checks if the agent is currently in lockdown mode."""
        return self.memory.get("lockdown_mode_active", False)

    def set_awaiting_intervention(self, issue_url: str = None):
        """
        Sets or clears the intervention flag.
        :param issue_url: The URL of the GitHub issue to wait on, or None to clear.
        """
        self.remember("awaiting_intervention_on_issue", issue_url)
        if issue_url:
            print(f"[INTERVENTION] Flag set. Awaiting resolution on {issue_url}")
        else:
            print("[INTERVENTION] Flag cleared.")

    def get_awaiting_intervention_url(self):
        """
        Returns the GitHub issue URL the agent is waiting on, or None if not waiting.
        """
        return self.memory.get("awaiting_intervention_on_issue")

if __name__ == '__main__':
    import time
    ltm = LongTermMemoryManager()
    print("--- Testing Observation Mode ---")
    print(f"Initially in observation mode: {ltm.is_in_observation_mode()}")
    ltm.set_observation_mode(days=0.00001) # Set for a very short time
    print(f"After setting, in observation mode: {ltm.is_in_observation_mode()}")
    time.sleep(1) # Wait for the mode to expire
    print(f"After waiting, in observation mode: {ltm.is_in_observation_mode()}")
    # Check that the key was cleared
    print(f"Value of observation_mode_until key: {ltm.recall('observation_mode_until')}")
