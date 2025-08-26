import os
import json
from google_drive_manager import GoogleDriveManager
from google_auth import fernet # Reusing the fernet object for encryption

class BackupManager:
    def __init__(self, settings):
        self.settings = settings
        self.provider = settings.get("backup_provider", "local")
        self.path = settings.get("backup_path", "data/backups")

    def backup(self, data, filename):
        """Encrypts the data and backs it up according to the selected provider."""
        try:
            # 1. Encrypt the data
            encrypted_data = fernet.encrypt(json.dumps(data, indent=2).encode())

            # 2. Save the encrypted data to a temporary file
            temp_file_path = os.path.join("data", f"{filename}.enc")
            with open(temp_file_path, 'wb') as f:
                f.write(encrypted_data)

            # 3. Call the appropriate backup method
            if self.provider == "local":
                result = self._backup_to_local(temp_file_path, f"{filename}.enc")
            elif self.provider == "google_drive":
                result = self._backup_to_google_drive(temp_file_path, f"{filename}.enc")
            else:
                result = f"Unknown backup provider: {self.provider}"
                # Clean up the temporary file even if the provider is unknown
                os.remove(temp_file_path)

            return result

        except Exception as e:
            # Clean up the temporary file in case of an error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return f"An error occurred during backup: {e}"

    def _backup_to_local(self, temp_file_path, filename):
        """Saves the backup file to a local path."""
        # Ensure the backup directory exists
        os.makedirs(self.path, exist_ok=True)

        destination_path = os.path.join(self.path, filename)
        # Use os.rename for atomic move
        os.rename(temp_file_path, destination_path)
        return f"Backup saved locally to '{destination_path}'."

    def _backup_to_google_drive(self, temp_file_path, filename):
        """Saves the backup file to Google Drive."""
        drive_manager = GoogleDriveManager()
        if not drive_manager.service:
            # Clean up the temporary file if Drive is not connected
            os.remove(temp_file_path)
            return "Google Drive not connected."

        drive_manager.save_file(temp_file_path, filename)
        # The temp file is uploaded, so now we can remove it
        os.remove(temp_file_path)
        return f"Backup saved to Google Drive as '{filename}'."
