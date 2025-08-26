import os
import json
import secrets

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
