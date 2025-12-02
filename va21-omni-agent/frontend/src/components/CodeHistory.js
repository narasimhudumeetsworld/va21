import React, { useState, useEffect, useCallback } from 'react';
import './CodeHistory.css';

const CodeHistory = () => {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [diff, setDiff] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState('all');
  const [viewMode, setViewMode] = useState('timeline'); // 'timeline' or 'diff'

  useEffect(() => {
    // Simulate loading code history data
    const mockFiles = [
      {
        path: 'src/components/App.js',
        versions: 12,
        lastModified: '2 hours ago',
        language: 'javascript'
      },
      {
        path: 'backend/server.py',
        versions: 8,
        lastModified: '1 day ago',
        language: 'python'
      },
      {
        path: 'src/utils/helpers.ts',
        versions: 5,
        lastModified: '3 hours ago',
        language: 'typescript'
      },
      {
        path: 'config/settings.json',
        versions: 3,
        lastModified: 'Just now',
        language: 'json'
      },
    ];

    setFiles(mockFiles);
    setStats({
      totalFiles: mockFiles.length,
      totalVersions: mockFiles.reduce((sum, f) => sum + f.versions, 0),
      storageUsed: '45.2 MB'
    });
    setLoading(false);
  }, []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setSelectedVersions([]);
    setDiff(null);
    
    // Mock versions for selected file
    const mockVersions = Array.from({ length: file.versions }, (_, i) => ({
      version_id: `v${file.versions - i}`,
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      description: i === 0 ? 'Latest changes' : `Auto-saved at ${new Date(Date.now() - i * 3600000).toLocaleTimeString()}`,
      lines_added: Math.floor(Math.random() * 50),
      lines_removed: Math.floor(Math.random() * 20),
      change_type: i === file.versions - 1 ? 'create' : 'modify',
      tags: i === 0 ? ['latest'] : [],
      age: i === 0 ? 'Just now' : `${i}h ago`
    }));
    
    setVersions(mockVersions);
    setViewMode('timeline');
  };

  const handleVersionSelect = (version) => {
    const isSelected = selectedVersions.includes(version.version_id);
    
    if (isSelected) {
      setSelectedVersions(prev => prev.filter(id => id !== version.version_id));
    } else if (selectedVersions.length < 2) {
      setSelectedVersions(prev => [...prev, version.version_id]);
    } else {
      setSelectedVersions([selectedVersions[1], version.version_id]);
    }
  };

  const handleCompare = () => {
    if (selectedVersions.length !== 2) return;
    
    // Mock diff
    setDiff({
      version_1: selectedVersions[0],
      version_2: selectedVersions[1],
      lines: [
        { type: 'context', content: 'import React from "react";' },
        { type: 'context', content: 'import "./App.css";' },
        { type: 'context', content: '' },
        { type: 'removed', content: '-const App = () => {' },
        { type: 'added', content: '+const App = ({ theme }) => {' },
        { type: 'context', content: '  const [state, setState] = useState(null);' },
        { type: 'added', content: '+  const [loading, setLoading] = useState(false);' },
        { type: 'context', content: '' },
        { type: 'removed', content: '-  return <div>Hello</div>;' },
        { type: 'added', content: '+  return (' },
        { type: 'added', content: '+    <div className={theme}>' },
        { type: 'added', content: '+      <h1>Hello World</h1>' },
        { type: 'added', content: '+    </div>' },
        { type: 'added', content: '+  );' },
        { type: 'context', content: '};' },
      ],
      stats: {
        lines_added: 6,
        lines_removed: 2
      }
    });
    setViewMode('diff');
  };

  const handleRestore = (version) => {
    if (window.confirm(`Restore ${selectedFile?.path} to version ${version.version_id}?`)) {
      setMessage({ text: `Restored to ${version.version_id}`, type: 'success' });
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const handleTag = (version, tag) => {
    setVersions(prev => prev.map(v => 
      v.version_id === version.version_id 
        ? { ...v, tags: [...v.tags, tag] }
        : v
    ));
    setMessage({ text: `Tagged as "${tag}"`, type: 'success' });
    setTimeout(() => setMessage(null), 3000);
  };

  const filteredFiles = files.filter(file => {
    if (searchQuery) {
      return file.path.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  const getLanguageIcon = (lang) => {
    const icons = {
      javascript: '🟨',
      typescript: '🔷',
      python: '🐍',
      json: '📋',
      css: '🎨',
      html: '🌐',
      default: '📄'
    };
    return icons[lang] || icons.default;
  };

  if (loading) {
    return (
      <div className="code-history-loading">
        <div className="loading-spinner">⏳</div>
        <p>Loading code history...</p>
      </div>
    );
  }

  return (
    <div className="code-history">
      <div className="code-history-header">
        <div className="header-info">
          <h2>📜 Code Version History</h2>
          <p className="subtitle">
            Track, compare, and restore your code changes
            {stats && (
              <span className="stats-info">
                {stats.totalFiles} files • {stats.totalVersions} versions • {stats.storageUsed}
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

      <div className="code-history-layout">
        {/* File List */}
        <div className="file-list-panel">
          <div className="panel-header">
            <h3>📁 Files</h3>
          </div>
          
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="file-list">
            {filteredFiles.map(file => (
              <div
                key={file.path}
                className={`file-item ${selectedFile?.path === file.path ? 'selected' : ''}`}
                onClick={() => handleFileSelect(file)}
              >
                <span className="file-icon">{getLanguageIcon(file.language)}</span>
                <div className="file-info">
                  <span className="file-path">{file.path}</span>
                  <span className="file-meta">
                    {file.versions} versions • {file.lastModified}
                  </span>
                </div>
              </div>
            ))}

            {filteredFiles.length === 0 && (
              <div className="no-files">
                <p>No files match your search</p>
              </div>
            )}
          </div>
        </div>

        {/* Version Timeline */}
        <div className="version-panel">
          {selectedFile ? (
            <>
              <div className="panel-header">
                <h3>🕐 Version Timeline</h3>
                <div className="panel-actions">
                  {selectedVersions.length === 2 && (
                    <button className="btn-compare" onClick={handleCompare}>
                      Compare Selected
                    </button>
                  )}
                </div>
              </div>

              {viewMode === 'timeline' ? (
                <div className="version-timeline">
                  {versions.map((version, index) => (
                    <div 
                      key={version.version_id}
                      className={`version-item ${selectedVersions.includes(version.version_id) ? 'selected' : ''}`}
                    >
                      <div 
                        className="version-marker"
                        onClick={() => handleVersionSelect(version)}
                      >
                        <div className={`marker-dot ${index === 0 ? 'latest' : ''}`} />
                        {index < versions.length - 1 && <div className="marker-line" />}
                      </div>
                      
                      <div className="version-content">
                        <div className="version-header">
                          <span className="version-id">{version.version_id}</span>
                          <span className="version-age">{version.age}</span>
                        </div>
                        
                        <p className="version-description">{version.description}</p>
                        
                        <div className="version-stats">
                          <span className="stat-added">+{version.lines_added}</span>
                          <span className="stat-removed">-{version.lines_removed}</span>
                          {version.tags.map(tag => (
                            <span key={tag} className="version-tag">{tag}</span>
                          ))}
                        </div>

                        <div className="version-actions">
                          <button 
                            className="btn-sm"
                            onClick={() => handleRestore(version)}
                          >
                            Restore
                          </button>
                          <button 
                            className="btn-sm btn-outline"
                            onClick={() => handleTag(version, 'important')}
                          >
                            Tag
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="diff-view">
                  <div className="diff-header">
                    <button 
                      className="btn-back"
                      onClick={() => setViewMode('timeline')}
                    >
                      ← Back to Timeline
                    </button>
                    <span className="diff-title">
                      Comparing {diff?.version_1} → {diff?.version_2}
                    </span>
                    {diff && (
                      <span className="diff-stats">
                        <span className="stat-added">+{diff.stats.lines_added}</span>
                        <span className="stat-removed">-{diff.stats.lines_removed}</span>
                      </span>
                    )}
                  </div>
                  
                  <div className="diff-content">
                    {diff?.lines.map((line, i) => (
                      <div key={i} className={`diff-line ${line.type}`}>
                        <span className="line-number">{i + 1}</span>
                        <span className="line-content">{line.content}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="no-selection">
              <span className="no-selection-icon">📂</span>
              <h3>Select a file</h3>
              <p>Choose a file from the list to view its version history</p>
            </div>
          )}
        </div>
      </div>

      <div className="code-history-footer">
        <p>
          💡 Tip: Select two versions and click "Compare" to see the diff between them
        </p>
      </div>
    </div>
  );
};

export default CodeHistory;
