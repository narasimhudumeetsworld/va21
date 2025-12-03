import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import SidePanel from './components/SidePanel/SidePanel';
import CommandPalette from './components/CommandPalette';
import { ThemeProvider, useTheme } from './components/ThemeProvider';
import './components/ThemeProvider.css';

// Import OS components
import Terminal from './components/Terminal';
import Settings from './components/Settings';
import AppCenter from './components/AppCenter';
import BackupManager from './components/BackupManager';
import ResearchCommandCenter from './components/ResearchCommandCenter';
import SystemStats from './components/SystemStats';

/**
 * VA21 OS - Main Application
 * 
 * This is a full operating system interface, NOT an Electron app.
 * The UI runs natively in the OS browser/display manager.
 * 
 * Om Vinayaka 🙏
 */

function AppContent() {
  const [isSidePanelOpen, setSidePanelOpen] = useState(true);
  const [isCommandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');
  const { theme, toggleTheme } = useTheme();

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Command Palette: Ctrl/Cmd + K
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      }
      // Alternative Command Palette: Ctrl/Cmd + Shift + P
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        setCommandPaletteOpen(prev => !prev);
      }
      // Toggle Side Panel: Ctrl/Cmd + B
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        setSidePanelOpen(prev => !prev);
      }
      // Toggle Theme: Ctrl/Cmd + Shift + T
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        toggleTheme();
      }
      // Terminal: Ctrl/Cmd + `
      if ((e.ctrlKey || e.metaKey) && e.key === '`') {
        e.preventDefault();
        setCurrentView('terminal');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    
    const handleThemeToggle = () => toggleTheme();
    window.addEventListener('toggle-theme', handleThemeToggle);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('toggle-theme', handleThemeToggle);
    };
  }, [toggleTheme]);

  const handleNavigate = useCallback((view) => {
    setCurrentView(view);
  }, []);

  const toggleSidePanel = useCallback(() => {
    setSidePanelOpen(prev => !prev);
  }, []);

  // Render the current view
  const renderMainContent = () => {
    switch (currentView) {
      case 'terminal':
        return <Terminal />;
      case 'settings':
        return <Settings />;
      case 'apps':
        return <AppCenter />;
      case 'backup':
        return <BackupManager />;
      case 'research':
        return <ResearchCommandCenter />;
      case 'stats':
        return <SystemStats />;
      case 'dashboard':
      default:
        return <Dashboard onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className={`va21-os ${theme}`}>
      {/* Top Bar */}
      <header className="va21-topbar">
        <div className="va21-topbar-left">
          <button 
            className="va21-menu-btn"
            onClick={toggleSidePanel}
            title="Toggle Menu (Ctrl+B)"
          >
            ☰
          </button>
          <span className="va21-logo">🔒 VA21 OS</span>
        </div>
        <div className="va21-topbar-center">
          <button 
            className="va21-command-btn"
            onClick={() => setCommandPaletteOpen(true)}
            title="Command Palette (Ctrl+K)"
          >
            🔍 Search or type a command...
          </button>
        </div>
        <div className="va21-topbar-right">
          <SystemStats compact />
          <button 
            className="va21-theme-btn"
            onClick={toggleTheme}
            title="Toggle Theme (Ctrl+Shift+T)"
          >
            {theme === 'dark' ? '🌙' : '☀️'}
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="va21-main">
        <SidePanel 
          isOpen={isSidePanelOpen} 
          onNavigate={handleNavigate}
          currentView={currentView}
        />
        <main className="va21-content">
          {renderMainContent()}
        </main>
      </div>

      {/* Command Palette */}
      <CommandPalette 
        isOpen={isCommandPaletteOpen} 
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={handleNavigate}
      />
    </div>
  );
}

/**
 * Dashboard - Main landing page for VA21 OS
 */
function Dashboard({ onNavigate }) {
  return (
    <div className="va21-dashboard">
      <div className="va21-welcome">
        <h1>🙏 Om Vinayaka</h1>
        <h2>Welcome to VA21 OS</h2>
        <p>Secure, AI-Powered Operating System</p>
      </div>

      <div className="va21-quick-actions">
        <h3>Quick Actions</h3>
        <div className="va21-action-grid">
          <button className="va21-action-card" onClick={() => onNavigate('terminal')}>
            <span className="va21-action-icon">💻</span>
            <span className="va21-action-label">Terminal</span>
            <span className="va21-action-desc">Zork-style interface</span>
          </button>
          <button className="va21-action-card" onClick={() => onNavigate('apps')}>
            <span className="va21-action-icon">📦</span>
            <span className="va21-action-label">App Center</span>
            <span className="va21-action-desc">Install applications</span>
          </button>
          <button className="va21-action-card" onClick={() => onNavigate('research')}>
            <span className="va21-action-icon">🔬</span>
            <span className="va21-action-label">Research</span>
            <span className="va21-action-desc">Knowledge vault</span>
          </button>
          <button className="va21-action-card" onClick={() => onNavigate('backup')}>
            <span className="va21-action-icon">💾</span>
            <span className="va21-action-label">Backup</span>
            <span className="va21-action-desc">System backups</span>
          </button>
          <button className="va21-action-card" onClick={() => onNavigate('settings')}>
            <span className="va21-action-icon">⚙️</span>
            <span className="va21-action-label">Settings</span>
            <span className="va21-action-desc">Configure system</span>
          </button>
          <button className="va21-action-card" onClick={() => onNavigate('stats')}>
            <span className="va21-action-icon">📊</span>
            <span className="va21-action-label">System Stats</span>
            <span className="va21-action-desc">Monitor resources</span>
          </button>
        </div>
      </div>

      <div className="va21-guardian-status">
        <h3>🛡️ Guardian AI Status</h3>
        <div className="va21-status-indicator active">
          <span className="va21-status-dot"></span>
          <span>Security Active - IBM Granite 4.0</span>
        </div>
        <p className="va21-status-desc">
          All systems protected. Think → Vet → Act methodology active.
        </p>
      </div>

      <div className="va21-features">
        <h3>Features</h3>
        <ul className="va21-feature-list">
          <li>✅ Meta Omnilingual ASR - 1,600+ languages</li>
          <li>✅ IBM Granite 4.0 - AI reasoning</li>
          <li>✅ Guardian AI - Security protection</li>
          <li>✅ Zork-style Terminal - Text adventure interface</li>
          <li>✅ Knowledge Vault - Research management</li>
          <li>✅ Privacy-first - No telemetry</li>
        </ul>
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
