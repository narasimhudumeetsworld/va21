import React, { useState } from 'react';
import './KeyboardShortcuts.css';

const KeyboardShortcuts = () => {
  const [activeCategory, setActiveCategory] = useState('all');

  const shortcuts = {
    navigation: [
      { keys: ['Ctrl/⌘', 'K'], description: 'Open Command Palette', action: 'Quick access to all commands' },
      { keys: ['Ctrl/⌘', 'Shift', 'P'], description: 'Open Command Palette (Alt)', action: 'Alternative shortcut' },
      { keys: ['Ctrl/⌘', '1'], description: 'Go to Chat', action: 'Navigate to Chat panel' },
      { keys: ['Ctrl/⌘', '2'], description: 'Go to Research', action: 'Navigate to Research Center' },
      { keys: ['Ctrl/⌘', '3'], description: 'Go to Terminals', action: 'Navigate to Terminals' },
      { keys: ['Ctrl/⌘', '4'], description: 'Go to Documents', action: 'Navigate to Documents' },
      { keys: ['Ctrl/⌘', '5'], description: 'Go to Settings', action: 'Navigate to Settings' },
      { keys: ['Ctrl/⌘', 'B'], description: 'Toggle Side Panel', action: 'Show/Hide side panel' },
      { keys: ['Esc'], description: 'Close Modal/Palette', action: 'Close any open modal or palette' },
    ],
    chat: [
      { keys: ['Enter'], description: 'Send Message', action: 'Send current message' },
      { keys: ['Shift', 'Enter'], description: 'New Line', action: 'Add new line in message' },
      { keys: ['Ctrl/⌘', 'L'], description: 'Clear Chat', action: 'Clear chat history' },
      { keys: ['Ctrl/⌘', 'E'], description: 'Export Chat', action: 'Export conversation' },
      { keys: ['↑'], description: 'Previous Message', action: 'Edit previous message' },
    ],
    research: [
      { keys: ['Ctrl/⌘', 'N'], description: 'New Note', action: 'Create a new note' },
      { keys: ['Ctrl/⌘', 'S'], description: 'Save Note', action: 'Save current note' },
      { keys: ['Ctrl/⌘', 'F'], description: 'Search Vault', action: 'Search in knowledge vault' },
      { keys: ['Ctrl/⌘', 'Shift', 'N'], description: 'New Research Session', action: 'Start new research' },
      { keys: ['Ctrl/⌘', 'G'], description: 'View Graph', action: 'View knowledge graph' },
    ],
    terminal: [
      { keys: ['Ctrl/⌘', 'T'], description: 'New Terminal', action: 'Open new terminal tab' },
      { keys: ['Ctrl/⌘', 'W'], description: 'Close Terminal', action: 'Close current terminal' },
      { keys: ['Ctrl', 'C'], description: 'Cancel Command', action: 'Cancel running command' },
      { keys: ['Ctrl', 'L'], description: 'Clear Terminal', action: 'Clear terminal screen' },
      { keys: ['Tab'], description: 'Auto-complete', action: 'Auto-complete command' },
      { keys: ['Ctrl/⌘', 'Shift', 'V'], description: 'Paste', action: 'Paste from clipboard' },
    ],
    backup: [
      { keys: ['Ctrl/⌘', 'Shift', 'S'], description: 'Create Backup', action: 'Create manual backup' },
      { keys: ['Ctrl/⌘', 'Shift', 'R'], description: 'Open Restore', action: 'Open restore dialog' },
      { keys: ['Ctrl/⌘', 'Shift', 'B'], description: 'Backup Manager', action: 'Open backup manager' },
    ],
    general: [
      { keys: ['Ctrl/⌘', ','], description: 'Settings', action: 'Open settings' },
      { keys: ['Ctrl/⌘', 'Shift', 'T'], description: 'Toggle Theme', action: 'Switch dark/light theme' },
      { keys: ['F11'], description: 'Fullscreen', action: 'Toggle fullscreen mode' },
      { keys: ['Ctrl/⌘', 'Q'], description: 'Quit', action: 'Quit application' },
      { keys: ['Ctrl/⌘', 'R'], description: 'Refresh', action: 'Refresh current view' },
      { keys: ['Ctrl/⌘', '?'], description: 'Help', action: 'Show keyboard shortcuts' },
    ],
  };

  const categories = [
    { id: 'all', label: 'All Shortcuts', icon: '⌨️' },
    { id: 'navigation', label: 'Navigation', icon: '🧭' },
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'research', label: 'Research', icon: '🔬' },
    { id: 'terminal', label: 'Terminal', icon: '💻' },
    { id: 'backup', label: 'Backup', icon: '💾' },
    { id: 'general', label: 'General', icon: '⚙️' },
  ];

  const getFilteredShortcuts = () => {
    if (activeCategory === 'all') {
      return Object.entries(shortcuts);
    }
    return [[activeCategory, shortcuts[activeCategory]]];
  };

  return (
    <div className="keyboard-shortcuts">
      <div className="shortcuts-header">
        <h2>⌨️ Keyboard Shortcuts</h2>
        <p className="shortcuts-subtitle">Master VA21 with these shortcuts</p>
      </div>

      <div className="shortcuts-categories">
        {categories.map(cat => (
          <button
            key={cat.id}
            className={`category-btn ${activeCategory === cat.id ? 'active' : ''}`}
            onClick={() => setActiveCategory(cat.id)}
          >
            <span className="category-icon">{cat.icon}</span>
            <span className="category-label">{cat.label}</span>
          </button>
        ))}
      </div>

      <div className="shortcuts-content">
        {getFilteredShortcuts().map(([category, categoryShortcuts]) => (
          <div key={category} className="shortcut-section">
            <h3 className="section-title">
              <span className="section-icon">
                {categories.find(c => c.id === category)?.icon || '📋'}
              </span>
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </h3>
            <div className="shortcuts-list">
              {categoryShortcuts.map((shortcut, idx) => (
                <div key={idx} className="shortcut-item">
                  <div className="shortcut-keys">
                    {shortcut.keys.map((key, keyIdx) => (
                      <React.Fragment key={keyIdx}>
                        <kbd className="key">{key}</kbd>
                        {keyIdx < shortcut.keys.length - 1 && (
                          <span className="key-separator">+</span>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                  <div className="shortcut-info">
                    <span className="shortcut-description">{shortcut.description}</span>
                    <span className="shortcut-action">{shortcut.action}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="shortcuts-footer">
        <div className="tip-card">
          <span className="tip-icon">💡</span>
          <div className="tip-content">
            <strong>Pro Tip:</strong> Use <kbd>Ctrl/⌘</kbd> + <kbd>K</kbd> to quickly access any command without remembering all shortcuts!
          </div>
        </div>
      </div>

      <div className="platform-note">
        <p>
          <strong>Note:</strong> Use <kbd>Ctrl</kbd> on Windows/Linux or <kbd>⌘</kbd> (Command) on macOS
        </p>
      </div>
    </div>
  );
};

export default KeyboardShortcuts;
