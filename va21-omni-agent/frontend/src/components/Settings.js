import React, { useState, useEffect } from 'react';
import './Settings.css';

function Settings() {
  const [provider, setProvider] = useState('ollama');
  const [url, setUrl] = useState('');
  const [apiKey, setApiKey] = useState('');

  useEffect(() => {
    fetch('/api/settings')
      .then((res) => res.json())
      .then((data) => {
        setProvider(data.provider || 'ollama');
        setUrl(data.url || '');
        setApiKey(data.api_key || '');
      });
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const settings = { provider, url, api_key: apiKey };
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

  return (
    <div className="settings">
      <h2>Settings</h2>
      <form onSubmit={handleSubmit}>
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

        <button type="submit">Save</button>
      </form>
    </div>
  );
}

export default Settings;
