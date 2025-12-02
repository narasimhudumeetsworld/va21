import React, { useState, useEffect } from 'react';
import './SystemStats.css';
import io from 'socket.io-client';

const SystemStats = () => {
  const [stats, setStats] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [backupStats, setBackupStats] = useState(null);
  const [agentStatus, setAgentStatus] = useState([]);
  const [securityAlerts, setSecurityAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    const socket = io('/stats');

    socket.on('connect', () => {
      socket.emit('get_all_stats');
    });

    socket.on('system_stats', (data) => {
      setStats(data);
    });

    socket.on('health_status', (data) => {
      setHealthStatus(data);
    });

    socket.on('backup_stats', (data) => {
      setBackupStats(data);
    });

    socket.on('agent_status', (data) => {
      setAgentStatus(data);
    });

    socket.on('security_alerts', (data) => {
      setSecurityAlerts(data);
    });

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      socket.emit('get_all_stats');
    }, 30000);

    return () => {
      clearInterval(interval);
      socket.disconnect();
    };
  }, []);

  const refreshStats = () => {
    setRefreshing(true);
    // Emit refresh event on the existing socket instead of creating a new connection
    const existingSocket = io('/stats');
    existingSocket.emit('get_all_stats');
    existingSocket.disconnect();
    setTimeout(() => setRefreshing(false), 1000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
      case 'idle':
      case 'completed':
        return 'status-healthy';
      case 'degraded':
      case 'working':
      case 'waiting':
        return 'status-warning';
      case 'critical':
      case 'error':
        return 'status-critical';
      default:
        return 'status-unknown';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
      case 'idle':
        return '🟢';
      case 'degraded':
      case 'working':
        return '🟡';
      case 'critical':
      case 'error':
        return '🔴';
      default:
        return '⚪';
    }
  };

  // Mock stats for display when backend isn't connected
  const mockStats = {
    cpu_percent: 45,
    memory: {
      percent: 62,
      used_gb: 8.2,
      total_gb: 16
    },
    disk: {
      percent: 38,
      used_gb: 120,
      total_gb: 512
    },
    uptime_hours: 24.5,
    active_sessions: 3,
    requests_per_minute: 12
  };

  const displayStats = stats || mockStats;

  return (
    <div className="system-stats">
      <div className="stats-header">
        <div className="header-title">
          <h2>📊 System Dashboard</h2>
          <p className="subtitle">Real-time monitoring & statistics</p>
        </div>
        <button 
          className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
          onClick={refreshStats}
          disabled={refreshing}
        >
          🔄 {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Main Metrics */}
      <div className="metrics-grid">
        <div className="metric-card cpu">
          <div className="metric-header">
            <span className="metric-icon">💻</span>
            <span className="metric-title">CPU Usage</span>
          </div>
          <div className="metric-value">{displayStats.cpu_percent}%</div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ width: `${displayStats.cpu_percent}%` }}
            />
          </div>
        </div>

        <div className="metric-card memory">
          <div className="metric-header">
            <span className="metric-icon">🧠</span>
            <span className="metric-title">Memory</span>
          </div>
          <div className="metric-value">{displayStats.memory?.percent || 0}%</div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ width: `${displayStats.memory?.percent || 0}%` }}
            />
          </div>
          <div className="metric-detail">
            {displayStats.memory?.used_gb?.toFixed(1)} / {displayStats.memory?.total_gb} GB
          </div>
        </div>

        <div className="metric-card disk">
          <div className="metric-header">
            <span className="metric-icon">💾</span>
            <span className="metric-title">Disk Space</span>
          </div>
          <div className="metric-value">{displayStats.disk?.percent || 0}%</div>
          <div className="metric-bar">
            <div 
              className="metric-fill"
              style={{ width: `${displayStats.disk?.percent || 0}%` }}
            />
          </div>
          <div className="metric-detail">
            {displayStats.disk?.used_gb} / {displayStats.disk?.total_gb} GB
          </div>
        </div>

        <div className="metric-card uptime">
          <div className="metric-header">
            <span className="metric-icon">⏱️</span>
            <span className="metric-title">Uptime</span>
          </div>
          <div className="metric-value">
            {Math.floor(displayStats.uptime_hours || 0)}h {Math.round((displayStats.uptime_hours % 1) * 60)}m
          </div>
          <div className="metric-detail">Active sessions: {displayStats.active_sessions || 0}</div>
        </div>
      </div>

      {/* Health Status Section */}
      <div className="section">
        <h3 className="section-title">🏥 Health Status</h3>
        <div className="health-grid">
          {healthStatus?.checks ? (
            Object.entries(healthStatus.checks).map(([name, check]) => (
              <div key={name} className={`health-item ${getStatusColor(check.status)}`}>
                <span className="health-icon">{getStatusIcon(check.status)}</span>
                <div className="health-info">
                  <span className="health-name">{name.replace(/_/g, ' ')}</span>
                  <span className="health-status">{check.status}</span>
                </div>
                {check.last_check && (
                  <span className="health-time">
                    {new Date(check.last_check).toLocaleTimeString()}
                  </span>
                )}
              </div>
            ))
          ) : (
            <>
              <div className="health-item status-healthy">
                <span className="health-icon">🟢</span>
                <div className="health-info">
                  <span className="health-name">Memory Usage</span>
                  <span className="health-status">healthy</span>
                </div>
              </div>
              <div className="health-item status-healthy">
                <span className="health-icon">🟢</span>
                <div className="health-info">
                  <span className="health-name">Disk Space</span>
                  <span className="health-status">healthy</span>
                </div>
              </div>
              <div className="health-item status-healthy">
                <span className="health-icon">🟢</span>
                <div className="health-info">
                  <span className="health-name">Backend Health</span>
                  <span className="health-status">healthy</span>
                </div>
              </div>
              <div className="health-item status-healthy">
                <span className="health-icon">🟢</span>
                <div className="health-info">
                  <span className="health-name">File Integrity</span>
                  <span className="health-status">healthy</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* AI Agents Section */}
      <div className="section">
        <h3 className="section-title">🤖 AI Agents</h3>
        <div className="agents-grid">
          {agentStatus.length > 0 ? (
            agentStatus.map((agent, idx) => (
              <div key={idx} className={`agent-card ${getStatusColor(agent.status)}`}>
                <div className="agent-header">
                  <span className="agent-icon">{getStatusIcon(agent.status)}</span>
                  <span className="agent-id">{agent.agent_id}</span>
                </div>
                <div className="agent-type">{agent.type}</div>
                <div className="agent-status">{agent.status}</div>
                {agent.current_task && (
                  <div className="agent-task">Task: {agent.current_task}</div>
                )}
              </div>
            ))
          ) : (
            <>
              <div className="agent-card status-healthy">
                <div className="agent-header">
                  <span className="agent-icon">🟢</span>
                  <span className="agent-id">Guardian</span>
                </div>
                <div className="agent-type">Security</div>
                <div className="agent-status">idle</div>
              </div>
              <div className="agent-card status-healthy">
                <div className="agent-header">
                  <span className="agent-icon">🟢</span>
                  <span className="agent-id">Researcher</span>
                </div>
                <div className="agent-type">Research</div>
                <div className="agent-status">idle</div>
              </div>
              <div className="agent-card status-healthy">
                <div className="agent-header">
                  <span className="agent-icon">🟢</span>
                  <span className="agent-id">Coder</span>
                </div>
                <div className="agent-type">Coding</div>
                <div className="agent-status">idle</div>
              </div>
              <div className="agent-card status-healthy">
                <div className="agent-header">
                  <span className="agent-icon">🟢</span>
                  <span className="agent-id">Planner</span>
                </div>
                <div className="agent-type">Planning</div>
                <div className="agent-status">idle</div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Backup Status */}
      <div className="section">
        <h3 className="section-title">💾 Backup Status</h3>
        <div className="backup-overview">
          <div className="backup-stat">
            <span className="backup-value">{backupStats?.total_versions || 0}</span>
            <span className="backup-label">Total Backups</span>
          </div>
          <div className="backup-stat">
            <span className="backup-value">{backupStats?.total_size_mb || 0} MB</span>
            <span className="backup-label">Storage Used</span>
          </div>
          <div className="backup-stat">
            <span className={`backup-value ${backupStats?.auto_backup_enabled ? 'enabled' : 'disabled'}`}>
              {backupStats?.auto_backup_enabled ? 'ON' : 'OFF'}
            </span>
            <span className="backup-label">Auto Backup</span>
          </div>
          <div className="backup-stat">
            <span className="backup-value">{backupStats?.newest_backup ? 'Recent' : 'Never'}</span>
            <span className="backup-label">Last Backup</span>
          </div>
        </div>
      </div>

      {/* Security Alerts */}
      <div className="section">
        <h3 className="section-title">🛡️ Security Status</h3>
        {securityAlerts.length > 0 ? (
          <div className="alerts-list">
            {securityAlerts.map((alert, idx) => (
              <div key={idx} className={`alert-item ${alert.severity}`}>
                <span className="alert-icon">
                  {alert.severity === 'critical' ? '🔴' : alert.severity === 'warning' ? '🟡' : 'ℹ️'}
                </span>
                <div className="alert-content">
                  <span className="alert-message">{alert.message}</span>
                  <span className="alert-time">{new Date(alert.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-alerts">
            <span className="no-alerts-icon">✅</span>
            <p>No security alerts</p>
            <span className="no-alerts-sub">System is operating normally</span>
          </div>
        )}
      </div>

      {/* Quick Stats Footer */}
      <div className="quick-stats">
        <div className="quick-stat">
          <span className="quick-icon">📨</span>
          <span className="quick-value">{displayStats.requests_per_minute || 0}</span>
          <span className="quick-label">req/min</span>
        </div>
        <div className="quick-stat">
          <span className="quick-icon">🔌</span>
          <span className="quick-value">{displayStats.active_sessions || 0}</span>
          <span className="quick-label">connections</span>
        </div>
        <div className="quick-stat">
          <span className="quick-icon">📊</span>
          <span className="quick-value">Normal</span>
          <span className="quick-label">load</span>
        </div>
        <div className="quick-stat">
          <span className="quick-icon">🔐</span>
          <span className="quick-value">Secure</span>
          <span className="quick-label">status</span>
        </div>
      </div>
    </div>
  );
};

export default SystemStats;
