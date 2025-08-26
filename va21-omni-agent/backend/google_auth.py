import os
import json
from cryptography.fernet import Fernet
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Scopes required for the application. Using drive.file for security.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'data/credentials.json.enc'
CLIENT_SECRET_FILE = 'client_secret.json' # User needs to provide this in the root of the backend
ENCRYPTION_KEY_FILE = 'data/encryption.key'

def get_encryption_key():
    """Loads the encryption key from a file, or generates a new one."""
    if os.path.exists(ENCRYPTION_KEY_FILE):
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            return f.read()
    else:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(ENCRYPTION_KEY_FILE), exist_ok=True)
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_FILE, 'wb') as f:
            f.write(key)
        return key

fernet = Fernet(get_encryption_key())

def save_credentials(credentials):
    """Saves and encrypts the user's credentials."""
    creds_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    encrypted_creds = fernet.encrypt(json.dumps(creds_dict).encode())
    with open(CREDENTIALS_FILE, 'wb') as f:
        f.write(encrypted_creds)

def load_credentials():
    """Loads and decrypts the user's credentials."""
    if not os.path.exists(CREDENTIALS_FILE):
        return None

    with open(CREDENTIALS_FILE, 'rb') as f:
        encrypted_creds = f.read()

    try:
        decrypted_creds = fernet.decrypt(encrypted_creds)
        creds_dict = json.loads(decrypted_creds)
        return Credentials(**creds_dict)
    except Exception as e:
        print(f"Error decrypting credentials: {e}")
        return None

def get_google_auth_flow():
    """Creates and returns a Google OAuth Flow object."""
    if not os.path.exists(CLIENT_SECRET_FILE):
        raise FileNotFoundError(f"'{CLIENT_SECRET_FILE}' not found. Please follow the instructions to create and download it from the Google Cloud Console and place it in the 'backend' directory.")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri='http://localhost:5000/api/google/callback'
    )
    return flow

def get_credentials():
    """
    Gets valid Google credentials.
    Refreshes the token if necessary.
    Returns None if no valid credentials are found.
    """
    credentials = load_credentials()
    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
            save_credentials(credentials)
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return None

    if credentials and credentials.valid:
        return credentials
    else:
        return None
