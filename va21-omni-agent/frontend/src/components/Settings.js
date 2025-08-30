import React, { useState, useEffect } from 'react';
import './Settings.css';

function Settings() {
  const [provider, setProvider] = useState('ollama');
  const [url, setUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [backupProvider, setBackupProvider] = useState('local');
  const [backupPath, setBackupPath] = useState('');
  const [githubPat, setGithubPat] = useState('');
  const [githubRepo, setGithubRepo] = useState('');

  useEffect(() => {
    // Fetch app settings via Electron IPC
    window.electronAPI.getSettings().then(data => {
        if (data) {
            setProvider(data.provider || 'ollama');
            setUrl(data.url || '');
            setApiKey(data.api_key || '');
            setBackupProvider(data.backup_provider || 'local');
            setBackupPath(data.backup_path || '');
            setGithubPat(data.github_pat || '');
            setGithubRepo(data.github_repo || '');
        }
    });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const settings = {
      provider,
      url,
      api_key: apiKey,
      backup_provider: backupProvider,
      backup_path: backupPath,
      github_pat: githubPat,
      github_repo: githubRepo
    };
    // Save app settings via Electron IPC
    window.electronAPI.saveSettings(settings);
    alert('Settings saved!');
  };

  return (
    <div className="settings">
      <h2>Settings</h2>
      <form onSubmit={handleSubmit}>
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

        <div className="setting-section">
          <h3>Services</h3>
          <div className="form-group">
            <label htmlFor="github-pat">GitHub Personal Access Token</label>
            <input
              type="password"
              id="github-pat"
              value={githubPat}
              onChange={(e) => setGithubPat(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="github-repo">GitHub Repository for Guardian</label>
            <input
              type="text"
              id="github-repo"
              value={githubRepo}
              onChange={(e) => setGithubRepo(e.target.value)}
              placeholder="e.g., owner/repo-name"
            />
          </div>
        </div>

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
              {/* Google Drive backup is disabled as it requires backend auth routes */}
              {/* <option value="google_drive">Google Drive</option> */}
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
        </div>

        <button type="submit">Save All Settings</button>
      </form>
    </div>
  );
}

export default Settings;
