import React, { useState, useEffect, useCallback } from 'react';
import './BackupManager.css';
import io from 'socket.io-client';

const BackupManager = () => {
  const [versions, setVersions] = useState([]);
  const [stats, setStats] = useState(null);
  const [config, setConfig] = useState({
    enabled: true,
    interval_minutes: 30,
    max_versions: 50,
    max_storage_mb: 500,
    compress_backups: true,
    backup_on_startup: true,
    backup_before_reset: true,
    auto_cleanup: true,
    retention_days: 30
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [restoreVersion, setRestoreVersion] = useState(null);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [filter, setFilter] = useState('all');

  const socket = io('/backup');

  useEffect(() => {
    // Connect and fetch initial data
    socket.on('connect', () => {
      console.log('Connected to backup server');
      socket.emit('get_versions');
      socket.emit('get_stats');
      socket.emit('get_config');
    });

    socket.on('versions_list', (data) => {
      setVersions(data);
    });

    socket.on('stats_update', (data) => {
      setStats(data);
    });

    socket.on('config_update', (data) => {
      setConfig(data);
    });

    socket.on('backup_created', (data) => {
      showMessage(`Backup created: ${data.version_id}`, 'success');
      socket.emit('get_versions');
      socket.emit('get_stats');
    });

    socket.on('restore_complete', (data) => {
      showMessage(`Restored from backup: ${data.version_id}`, 'success');
      setShowRestoreModal(false);
      setLoading(false);
    });

    socket.on('error', (data) => {
      showMessage(data.message, 'error');
      setLoading(false);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const createBackup = useCallback((description = '', backupType = 'manual') => {
    setLoading(true);
    socket.emit('create_backup', { description, backup_type: backupType });
  }, [socket]);

  const createPreResetBackup = useCallback(() => {
    setLoading(true);
    socket.emit('create_pre_reset_backup');
  }, [socket]);

  const restoreBackup = useCallback((versionId, components = null) => {
    setLoading(true);
    socket.emit('restore_backup', { version_id: versionId, components });
  }, [socket]);

  const deleteVersion = useCallback((versionId) => {
    if (window.confirm('Are you sure you want to delete this backup version?')) {
      socket.emit('delete_version', { version_id: versionId });
      socket.emit('get_versions');
      socket.emit('get_stats');
    }
  }, [socket]);

  const deleteSelected = useCallback(() => {
    if (selectedVersions.length === 0) return;
    if (window.confirm(`Delete ${selectedVersions.length} selected backup(s)?`)) {
      selectedVersions.forEach(id => {
        socket.emit('delete_version', { version_id: id });
      });
      setSelectedVersions([]);
      setTimeout(() => {
        socket.emit('get_versions');
        socket.emit('get_stats');
      }, 500);
    }
  }, [socket, selectedVersions]);

  const updateConfig = useCallback((newConfig) => {
    socket.emit('update_config', newConfig);
    setShowConfigModal(false);
  }, [socket]);

  const toggleAutoBackup = useCallback(() => {
    const newConfig = { ...config, enabled: !config.enabled };
    socket.emit('update_config', newConfig);
  }, [socket, config]);

  const toggleVersionSelection = (versionId) => {
    setSelectedVersions(prev => 
      prev.includes(versionId) 
        ? prev.filter(id => id !== versionId)
        : [...prev, versionId]
    );
  };

  const filteredVersions = versions.filter(v => {
    if (filter === 'all') return true;
    return v.backup_type === filter;
  });

  const getTypeIcon = (type) => {
    switch (type) {
      case 'auto': return '🔄';
      case 'manual': return '💾';
      case 'pre-reset': return '🛡️';
      default: return '📁';
    }
  };

  const getTypeBadgeClass = (type) => {
    switch (type) {
      case 'auto': return 'badge-auto';
      case 'manual': return 'badge-manual';
      case 'pre-reset': return 'badge-prereset';
      default: return '';
    }
  };

  return (
    <div className="backup-manager">
      <div className="backup-header">
        <div className="header-title">
          <h2>💾 Backup Manager</h2>
          <p className="subtitle">Version History & Restore</p>
        </div>
        <div className="header-actions">
          <button 
            className={`auto-backup-toggle ${config.enabled ? 'enabled' : 'disabled'}`}
            onClick={toggleAutoBackup}
          >
            {config.enabled ? '🟢 Auto Backup ON' : '🔴 Auto Backup OFF'}
          </button>
          <button className="btn-settings" onClick={() => setShowConfigModal(true)}>
            ⚙️ Settings
          </button>
        </div>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      {stats && (
        <div className="backup-stats">
          <div className="stat-card">
            <span className="stat-icon">📊</span>
            <div className="stat-content">
              <span className="stat-value">{stats.total_versions}</span>
              <span className="stat-label">Total Backups</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">💿</span>
            <div className="stat-content">
              <span className="stat-value">{stats.total_size_mb} MB</span>
              <span className="stat-label">Storage Used</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">📈</span>
            <div className="stat-content">
              <div className="storage-bar">
                <div 
                  className="storage-fill"
                  style={{ width: `${Math.min(stats.storage_used_percent, 100)}%` }}
                />
              </div>
              <span className="stat-label">{stats.storage_used_percent}% of {stats.max_storage_mb} MB</span>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">⏰</span>
            <div className="stat-content">
              <span className="stat-value">{config.interval_minutes} min</span>
              <span className="stat-label">Backup Interval</span>
            </div>
          </div>
        </div>
      )}

      <div className="backup-actions">
        <button 
          className="btn-primary"
          onClick={() => createBackup('Manual backup', 'manual')}
          disabled={loading}
        >
          💾 Create Backup
        </button>
        <button 
          className="btn-warning"
          onClick={createPreResetBackup}
          disabled={loading}
        >
          🛡️ Pre-Reset Backup
        </button>
        {selectedVersions.length > 0 && (
          <button 
            className="btn-danger"
            onClick={deleteSelected}
          >
            🗑️ Delete Selected ({selectedVersions.length})
          </button>
        )}
      </div>

      <div className="backup-filters">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button 
          className={`filter-btn ${filter === 'auto' ? 'active' : ''}`}
          onClick={() => setFilter('auto')}
        >
          🔄 Auto
        </button>
        <button 
          className={`filter-btn ${filter === 'manual' ? 'active' : ''}`}
          onClick={() => setFilter('manual')}
        >
          💾 Manual
        </button>
        <button 
          className={`filter-btn ${filter === 'pre-reset' ? 'active' : ''}`}
          onClick={() => setFilter('pre-reset')}
        >
          🛡️ Pre-Reset
        </button>
      </div>

      <div className="versions-list">
        {filteredVersions.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📂</span>
            <h3>No backups found</h3>
            <p>Create your first backup to get started</p>
            <button onClick={() => createBackup('First backup', 'manual')}>
              Create Backup
            </button>
          </div>
        ) : (
          <table className="versions-table">
            <thead>
              <tr>
                <th className="col-select">
                  <input 
                    type="checkbox"
                    checked={selectedVersions.length === filteredVersions.length}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedVersions(filteredVersions.map(v => v.version_id));
                      } else {
                        setSelectedVersions([]);
                      }
                    }}
                  />
                </th>
                <th>Type</th>
                <th>Description</th>
                <th>Date</th>
                <th>Age</th>
                <th>Size</th>
                <th>Components</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredVersions.map(version => (
                <tr 
                  key={version.version_id}
                  className={selectedVersions.includes(version.version_id) ? 'selected' : ''}
                >
                  <td className="col-select">
                    <input 
                      type="checkbox"
                      checked={selectedVersions.includes(version.version_id)}
                      onChange={() => toggleVersionSelection(version.version_id)}
                    />
                  </td>
                  <td>
                    <span className={`type-badge ${getTypeBadgeClass(version.backup_type)}`}>
                      {getTypeIcon(version.backup_type)} {version.backup_type}
                    </span>
                  </td>
                  <td className="col-description">{version.description}</td>
                  <td className="col-date">
                    {new Date(version.timestamp).toLocaleString()}
                  </td>
                  <td className="col-age">{version.age}</td>
                  <td className="col-size">{version.size_formatted}</td>
                  <td className="col-components">
                    <span className="component-count">
                      {version.components.length} items
                    </span>
                  </td>
                  <td className="col-actions">
                    <button 
                      className="btn-restore"
                      onClick={() => {
                        setRestoreVersion(version);
                        setShowRestoreModal(true);
                      }}
                      title="Restore"
                    >
                      ⏪
                    </button>
                    <button 
                      className="btn-delete"
                      onClick={() => deleteVersion(version.version_id)}
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Restore Modal */}
      {showRestoreModal && restoreVersion && (
        <div className="modal-overlay" onClick={() => setShowRestoreModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>⏪ Restore Backup</h3>
            <div className="restore-info">
              <p><strong>Version:</strong> {restoreVersion.version_id}</p>
              <p><strong>Created:</strong> {new Date(restoreVersion.timestamp).toLocaleString()}</p>
              <p><strong>Description:</strong> {restoreVersion.description}</p>
            </div>
            
            <div className="restore-components">
              <h4>Components to restore:</h4>
              <div className="component-list">
                {restoreVersion.components.map(comp => (
                  <label key={comp} className="component-item">
                    <input type="checkbox" defaultChecked />
                    <span>{comp}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="restore-warning">
              ⚠️ A safety backup will be created before restoring.
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowRestoreModal(false)}>
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={() => restoreBackup(restoreVersion.version_id)}
                disabled={loading}
              >
                {loading ? 'Restoring...' : 'Restore Now'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Config Modal */}
      {showConfigModal && (
        <div className="modal-overlay" onClick={() => setShowConfigModal(false)}>
          <div className="modal config-modal" onClick={e => e.stopPropagation()}>
            <h3>⚙️ Backup Settings</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              updateConfig(config);
            }}>
              <div className="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={config.enabled}
                    onChange={(e) => setConfig({...config, enabled: e.target.checked})}
                  />
                  Enable Auto Backup
                </label>
              </div>

              <div className="form-group">
                <label>Backup Interval (minutes)</label>
                <input 
                  type="number" 
                  min="5" 
                  max="1440"
                  value={config.interval_minutes}
                  onChange={(e) => setConfig({...config, interval_minutes: parseInt(e.target.value)})}
                />
              </div>

              <div className="form-group">
                <label>Maximum Versions</label>
                <input 
                  type="number" 
                  min="5" 
                  max="200"
                  value={config.max_versions}
                  onChange={(e) => setConfig({...config, max_versions: parseInt(e.target.value)})}
                />
              </div>

              <div className="form-group">
                <label>Maximum Storage (MB)</label>
                <input 
                  type="number" 
                  min="100" 
                  max="5000"
                  value={config.max_storage_mb}
                  onChange={(e) => setConfig({...config, max_storage_mb: parseInt(e.target.value)})}
                />
              </div>

              <div className="form-group">
                <label>Retention Days</label>
                <input 
                  type="number" 
                  min="1" 
                  max="365"
                  value={config.retention_days}
                  onChange={(e) => setConfig({...config, retention_days: parseInt(e.target.value)})}
                />
              </div>

              <div className="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={config.compress_backups}
                    onChange={(e) => setConfig({...config, compress_backups: e.target.checked})}
                  />
                  Compress Backups
                </label>
              </div>

              <div className="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={config.backup_on_startup}
                    onChange={(e) => setConfig({...config, backup_on_startup: e.target.checked})}
                  />
                  Backup on Startup
                </label>
              </div>

              <div className="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={config.backup_before_reset}
                    onChange={(e) => setConfig({...config, backup_before_reset: e.target.checked})}
                  />
                  Backup Before Reset
                </label>
              </div>

              <div className="form-group">
                <label>
                  <input 
                    type="checkbox" 
                    checked={config.auto_cleanup}
                    onChange={(e) => setConfig({...config, auto_cleanup: e.target.checked})}
                  />
                  Auto Cleanup Old Backups
                </label>
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setShowConfigModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Settings
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackupManager;
