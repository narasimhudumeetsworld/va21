import React, { useState, useEffect } from 'react';
import './Settings.css';

function Settings() {
  const [provider, setProvider] = useState('ollama');
  const [url, setUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [googleConnected, setGoogleConnected] = useState(false);
  const [backupProvider, setBackupProvider] = useState('local');
  const [backupPath, setBackupPath] = useState('');

  useEffect(() => {
    // Fetch app settings
    fetch('/api/settings')
      .then((res) => res.json())
      .then((data) => {
        setProvider(data.provider || 'ollama');
        setUrl(data.url || '');
        setApiKey(data.api_key || '');
        setBackupProvider(data.backup_provider || 'local');
        setBackupPath(data.backup_path || '');
      });

    // Fetch Google connection status
    fetch('/api/google/status')
      .then((res) => res.json())
      .then((data) => {
        setGoogleConnected(data.status === 'connected');
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const settings = {
      provider,
      url,
      api_key: apiKey,
      backup_provider: backupProvider,
      backup_path: backupPath
    };
    fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message || data.error);
      });
  };

  const handleGoogleConnect = () => {
    window.location.href = '/api/google/auth';
  };

  return (
    <div className="settings">
      <h2>Settings</h2>
      <form onSubmit={handleSubmit}>
        <div className="setting-section">
          <h3>Backup Settings</h3>
          <div className="form-group">
            <label htmlFor="backup-provider">Backup Provider</label>
            <select
              id="backup-provider"
              value={backupProvider}
              onChange={(e) => setBackupProvider(e.target.value)}
            >
              <option value="local">Local</option>
              <option value="google_drive">Google Drive</option>
            </select>
          </div>
          {backupProvider === 'local' && (
            <div className="form-group">
              <label htmlFor="backup-path">Local Backup Path</label>
              <input
                type="text"
                id="backup-path"
                value={backupPath}
                onChange={(e) => setBackupPath(e.target.value)}
                placeholder="/path/to/your/backup/folder"
              />
            </div>
          )}
          {backupProvider === 'google_drive' && (
            <div className="form-group">
              {googleConnected ? (
                <p>Connected to Google Drive.</p>
              ) : (
                <button type="button" onClick={handleGoogleConnect}>Connect to Google</button>
              )}
            </div>
          )}
        </div>

        <div className="setting-section">
          <h3>LLM Provider</h3>
          <div className="form-group">
            <label htmlFor="provider">LLM Provider</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
            >
              <option value="ollama">Ollama</option>
              <option value="authenticated_ollama">Authenticated Ollama</option>
              <option value="gemini">Gemini</option>
            </select>
          </div>

          {(provider === 'ollama' || provider === 'authenticated_ollama') && (
            <div className="form-group">
              <label htmlFor="url">API URL</label>
              <input
                type="text"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
          )}

          {(provider === 'authenticated_ollama' || provider === 'gemini') && (
            <div className="form-group">
              <label htmlFor="api-key">API Key</label>
              <input
                type="password"
                id="api-key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
            </div>
          )}
        </div>

        <button type="submit">Save All Settings</button>
      </form>
    </div>
  );
}

export default Settings;
