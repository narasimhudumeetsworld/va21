from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import google_auth
import os

class GoogleDriveManager:
    def __init__(self):
        self.credentials = google_auth.get_credentials()
        if self.credentials:
            self.service = build('drive', 'v3', credentials=self.credentials)
        else:
            self.service = None

    def save_file(self, file_path, file_name, folder_name="OmniAgentBackup"):
        """Saves a file to a specific folder in Google Drive. Updates the file if it already exists."""
        if not self.service:
            print("Google Drive not connected.")
            return None

        try:
            # 1. Find or create the folder
            folder_id = self.find_or_create_folder(folder_name)

            # 2. Search for the file in the folder
            file_id = self.find_file_in_folder(file_name, folder_id)

            media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)

            if file_id:
                # File exists, update it
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
                print(f"File '{file_name}' updated in Google Drive folder '{folder_name}'.")
                return file_id
            else:
                # File does not exist, create it
                file_metadata = {'name': file_name, 'parents': [folder_id]}
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                print(f"File '{file_name}' created in Google Drive folder '{folder_name}'.")
                return file.get('id')
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def find_or_create_folder(self, folder_name):
        """Finds a folder by name, or creates it if it doesn't exist."""
        response = self.service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id)'
        ).execute()

        files = response.get('files', [])
        if files:
            return files[0].get('id')
        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')

    def find_file_in_folder(self, file_name, folder_id):
        """Finds a file by name within a specific folder."""
        response = self.service.files().list(
            q=f"name='{file_name}' and '{folder_id}' in parents and trashed=false",
            spaces='drive',
            fields='files(id)'
        ).execute()

        files = response.get('files', [])
        if files:
            return files[0].get('id')
        else:
            return None
