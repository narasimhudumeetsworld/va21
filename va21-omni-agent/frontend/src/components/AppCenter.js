import React, { useState, useEffect, useCallback } from 'react';
import './AppCenter.css';
import io from 'socket.io-client';

const AppCenter = () => {
  const [apps, setApps] = useState([]);
  const [featuredApps, setFeaturedApps] = useState([]);
  const [categories, setCategories] = useState(['All']);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedSource, setSelectedSource] = useState('all');
  const [loading, setLoading] = useState(false);
  const [installing, setInstalling] = useState({});
  const [selectedApp, setSelectedApp] = useState(null);
  const [message, setMessage] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);

  useEffect(() => {
    const socket = io('/apps');

    socket.on('connect', () => {
      socket.emit('get_featured_apps');
      socket.emit('get_categories');
      socket.emit('get_system_info');
    });

    socket.on('featured_apps', (data) => {
      setFeaturedApps(data);
      if (!searchQuery) {
        setApps(data);
      }
    });

    socket.on('categories', (data) => {
      setCategories(data);
    });

    socket.on('search_results', (data) => {
      setApps(data);
      setLoading(false);
    });

    socket.on('system_info', (data) => {
      setSystemInfo(data);
    });

    socket.on('install_progress', (data) => {
      setInstalling(prev => ({
        ...prev,
        [data.app_id]: data.progress
      }));
    });

    socket.on('install_complete', (data) => {
      setInstalling(prev => {
        const newState = { ...prev };
        delete newState[data.app_id];
        return newState;
      });
      showMessage(data.message, data.success ? 'success' : 'error');
      // Refresh app list
      socket.emit('get_featured_apps');
    });

    socket.on('error', (data) => {
      showMessage(data.message, 'error');
      setLoading(false);
    });

    return () => socket.disconnect();
  }, []);

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
    if (query.trim()) {
      setLoading(true);
      const socket = io('/apps');
      socket.emit('search_apps', {
        query,
        source: selectedSource,
        category: selectedCategory
      });
    } else {
      setApps(featuredApps);
    }
  }, [selectedSource, selectedCategory, featuredApps]);

  const handleInstall = useCallback((app) => {
    const socket = io('/apps');
    setInstalling(prev => ({ ...prev, [app.id]: 0 }));
    socket.emit('install_app', {
      app_id: app.id,
      source: app.source
    });
  }, []);

  const handleUninstall = useCallback((app) => {
    if (window.confirm(`Uninstall ${app.name}?`)) {
      const socket = io('/apps');
      socket.emit('uninstall_app', {
        app_id: app.id,
        source: app.source
      });
    }
  }, []);

  const getSourceIcon = (source) => {
    switch (source) {
      case 'flatpak': return '📦';
      case 'debian': return '🐧';
      default: return '📦';
    }
  };

  const filteredApps = apps.filter(app => {
    if (selectedCategory !== 'All' && app.category !== selectedCategory) {
      return false;
    }
    if (selectedSource !== 'all' && app.source !== selectedSource) {
      return false;
    }
    return true;
  });

  return (
    <div className="app-center">
      <div className="app-center-header">
        <div className="header-title">
          <h2>📦 App Center</h2>
          <p className="subtitle">
            Discover and install applications
            {systemInfo && (
              <span className="system-badge">
                {systemInfo.flatpak_available && '📦 Flatpak'}
                {systemInfo.apt_available && ' 🐧 Debian'}
              </span>
            )}
          </p>
        </div>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="search-section">
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search apps..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input"
          />
          {loading && <span className="loading-spinner">⏳</span>}
        </div>

        <div className="filters">
          <select
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Sources</option>
            <option value="flatpak">📦 Flatpak</option>
            <option value="debian">🐧 Debian</option>
          </select>

          <div className="category-pills">
            {categories.map(cat => (
              <button
                key={cat}
                className={`category-pill ${selectedCategory === cat ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {!searchQuery && (
        <div className="featured-section">
          <h3>✨ Featured Apps</h3>
          <div className="featured-grid">
            {featuredApps.slice(0, 6).map(app => (
              <div
                key={app.id}
                className="featured-card"
                onClick={() => setSelectedApp(app)}
              >
                <span className="app-icon-large">{app.icon}</span>
                <div className="app-info">
                  <span className="app-name">{app.name}</span>
                  <span className="app-category">{app.category}</span>
                </div>
                <span className={`source-badge ${app.source}`}>
                  {getSourceIcon(app.source)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="apps-grid">
        {filteredApps.map(app => (
          <div key={app.id} className="app-card">
            <div className="app-card-header">
              <span className="app-icon">{app.icon || '📦'}</span>
              <div className="app-details">
                <span className="app-name">{app.name}</span>
                <span className="app-summary">{app.summary}</span>
              </div>
              <span className={`source-badge ${app.source}`}>
                {getSourceIcon(app.source)}
              </span>
            </div>

            <div className="app-card-footer">
              <span className="app-category-tag">{app.category}</span>
              
              {installing[app.id] !== undefined ? (
                <div className="install-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${installing[app.id]}%` }}
                    />
                  </div>
                  <span className="progress-text">Installing...</span>
                </div>
              ) : app.installed ? (
                <div className="installed-actions">
                  <span className="installed-badge">✓ Installed</span>
                  <button
                    className="btn-uninstall"
                    onClick={() => handleUninstall(app)}
                  >
                    🗑️
                  </button>
                </div>
              ) : (
                <button
                  className="btn-install"
                  onClick={() => handleInstall(app)}
                >
                  Install
                </button>
              )}
            </div>
          </div>
        ))}

        {filteredApps.length === 0 && !loading && (
          <div className="no-apps">
            <span className="no-apps-icon">📭</span>
            <h3>No apps found</h3>
            <p>Try a different search term or category</p>
          </div>
        )}
      </div>

      {selectedApp && (
        <div className="app-modal-overlay" onClick={() => setSelectedApp(null)}>
          <div className="app-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedApp(null)}>×</button>
            
            <div className="app-modal-header">
              <span className="app-icon-xl">{selectedApp.icon || '📦'}</span>
              <div className="app-modal-info">
                <h2>{selectedApp.name}</h2>
                <span className="developer">{selectedApp.developer || 'Unknown Developer'}</span>
                <div className="badges">
                  <span className={`source-badge ${selectedApp.source}`}>
                    {getSourceIcon(selectedApp.source)} {selectedApp.source}
                  </span>
                  <span className="category-badge">{selectedApp.category}</span>
                </div>
              </div>
            </div>

            <div className="app-modal-body">
              <p className="app-description">
                {selectedApp.description || selectedApp.summary}
              </p>
              
              {selectedApp.size && (
                <div className="app-meta">
                  <span>Size: {selectedApp.size}</span>
                </div>
              )}
            </div>

            <div className="app-modal-footer">
              {installing[selectedApp.id] !== undefined ? (
                <div className="install-progress-large">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${installing[selectedApp.id]}%` }}
                    />
                  </div>
                  <span>Installing... {installing[selectedApp.id]}%</span>
                </div>
              ) : selectedApp.installed ? (
                <>
                  <span className="installed-status">✓ Installed</span>
                  <button
                    className="btn-uninstall-large"
                    onClick={() => handleUninstall(selectedApp)}
                  >
                    Uninstall
                  </button>
                </>
              ) : (
                <button
                  className="btn-install-large"
                  onClick={() => handleInstall(selectedApp)}
                >
                  Install Now
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="app-center-footer">
        <p>
          Thanks to <strong>Debian Project</strong>, <strong>Linux Foundation</strong>, 
          and the <strong>Linux Community</strong> 🐧❤️
        </p>
        <p className="powered-by">
          Powered by Flathub & Debian Repositories
        </p>
      </div>
    </div>
  );
};

export default AppCenter;
