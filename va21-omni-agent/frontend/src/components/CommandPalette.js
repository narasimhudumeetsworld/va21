import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import './CommandPalette.css';

const CommandPalette = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  const commands = [
    // Navigation
    { id: 'nav-chat', label: 'Go to Chat', category: 'Navigation', icon: '💬', action: () => navigate('/') },
    { id: 'nav-research', label: 'Go to Research Center', category: 'Navigation', icon: '🔬', action: () => navigate('/research') },
    { id: 'nav-terminals', label: 'Go to Terminals', category: 'Navigation', icon: '📟', action: () => navigate('/terminals') },
    { id: 'nav-terminal', label: 'Go to Terminal', category: 'Navigation', icon: '💻', action: () => navigate('/terminal') },
    { id: 'nav-documents', label: 'Go to Documents', category: 'Navigation', icon: '📄', action: () => navigate('/documents') },
    { id: 'nav-workflows', label: 'Go to Workflows', category: 'Navigation', icon: '⚙️', action: () => navigate('/workflows') },
    { id: 'nav-settings', label: 'Go to Settings', category: 'Navigation', icon: '⚙️', action: () => navigate('/settings') },
    { id: 'nav-stats', label: 'Go to System Stats', category: 'Navigation', icon: '📊', action: () => navigate('/stats') },
    { id: 'nav-bookmarks', label: 'Go to Bookmarks', category: 'Navigation', icon: '🔖', action: () => navigate('/bookmarks') },
    { id: 'nav-shortcuts', label: 'Show Keyboard Shortcuts', category: 'Navigation', icon: '⌨️', action: () => navigate('/shortcuts') },
    
    // Actions
    { id: 'action-new-note', label: 'Create New Note', category: 'Actions', icon: '📝', action: () => console.log('New note') },
    { id: 'action-new-research', label: 'Start New Research Session', category: 'Actions', icon: '🔬', action: () => console.log('New research') },
    { id: 'action-export', label: 'Export Data', category: 'Actions', icon: '📤', action: () => console.log('Export data') },
    { id: 'action-backup', label: 'Create Backup', category: 'Actions', icon: '💾', action: () => console.log('Create backup') },
    { id: 'action-sync', label: 'Sync Knowledge Graph', category: 'Actions', icon: '🔄', action: () => console.log('Sync graph') },
    
    // Quick Settings
    { id: 'toggle-theme', label: 'Toggle Dark/Light Theme', category: 'Settings', icon: '🌓', action: () => {
      const event = new CustomEvent('toggle-theme');
      window.dispatchEvent(event);
    }},
    { id: 'clear-history', label: 'Clear Chat History', category: 'Settings', icon: '🗑️', action: () => console.log('Clear history') },
  ];

  const filteredCommands = commands.filter(cmd => 
    cmd.label.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = [];
    }
    acc[cmd.category].push(cmd);
    return acc;
  }, {});

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
    setQuery('');
    setSelectedIndex(0);
  }, [isOpen]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
        onClose();
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  }, [filteredCommands, selectedIndex, onClose]);

  const executeCommand = (command) => {
    command.action();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={e => e.stopPropagation()}>
        <div className="command-palette-header">
          <span className="command-palette-icon">⌘</span>
          <input
            ref={inputRef}
            type="text"
            className="command-palette-input"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
          />
          <span className="command-palette-hint">ESC to close</span>
        </div>
        
        <div className="command-palette-content">
          {Object.entries(groupedCommands).map(([category, cmds]) => (
            <div key={category} className="command-group">
              <div className="command-group-title">{category}</div>
              {cmds.map((cmd, idx) => {
                const globalIndex = filteredCommands.indexOf(cmd);
                return (
                  <div
                    key={cmd.id}
                    className={`command-item ${globalIndex === selectedIndex ? 'selected' : ''}`}
                    onClick={() => executeCommand(cmd)}
                    onMouseEnter={() => setSelectedIndex(globalIndex)}
                  >
                    <span className="command-icon">{cmd.icon}</span>
                    <span className="command-label">{cmd.label}</span>
                    <span className="command-shortcut">↵</span>
                  </div>
                );
              })}
            </div>
          ))}
          
          {filteredCommands.length === 0 && (
            <div className="command-empty">
              <span className="command-empty-icon">🔍</span>
              <p>No commands found for "{query}"</p>
            </div>
          )}
        </div>
        
        <div className="command-palette-footer">
          <span><kbd>↑</kbd><kbd>↓</kbd> Navigate</span>
          <span><kbd>↵</kbd> Select</span>
          <span><kbd>Esc</kbd> Close</span>
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;
