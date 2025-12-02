import React, { useState, useEffect, useCallback } from 'react';
import './DeveloperTools.css';

const DeveloperTools = () => {
  const [tools, setTools] = useState({});
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState({});
  const [message, setMessage] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState(null);

  const categories = [
    { id: 'all', label: 'All Tools', icon: '🔧' },
    { id: 'gnu_core', label: 'GNU Core', icon: '🐃' },
    { id: 'build_tools', label: 'Build Tools', icon: '🏗️' },
    { id: 'version_control', label: 'Version Control', icon: '📝' },
    { id: 'languages', label: 'Languages', icon: '💻' },
    { id: 'containers', label: 'Containers', icon: '🐳' },
    { id: 'databases', label: 'Databases', icon: '💾' },
    { id: 'editors', label: 'Editors', icon: '📝' },
    { id: 'networking', label: 'Networking', icon: '🌐' },
    { id: 'utilities', label: 'Utilities', icon: '🛠️' },
    { id: 'documentation', label: 'Documentation', icon: '📚' },
  ];

  const bundles = [
    { id: 'full_gnu_toolkit', name: 'Full GNU Toolkit', description: 'Complete GNU development environment', icon: '🐃' },
    { id: 'c_cpp_development', name: 'C/C++ Development', description: 'GCC, GDB, CMake, Valgrind', icon: '⚙️' },
    { id: 'python_development', name: 'Python Development', description: 'Python 3, pip, venv, dev tools', icon: '🐍' },
    { id: 'web_development', name: 'Web Development', description: 'Node.js, npm, Git, curl', icon: '🌐' },
    { id: 'rust_development', name: 'Rust Development', description: 'Rust compiler and cargo', icon: '🦀' },
    { id: 'go_development', name: 'Go Development', description: 'Go language and tools', icon: '🐹' },
    { id: 'java_development', name: 'Java Development', description: 'JDK, Maven, Gradle', icon: '☕' },
    { id: 'devops', name: 'DevOps', description: 'Docker, Git, Ansible', icon: '🚀' },
    { id: 'database', name: 'Database Tools', description: 'PostgreSQL, MySQL, Redis clients', icon: '💾' },
  ];

  useEffect(() => {
    // Simulate loading tools data
    // In real implementation, this would fetch from backend
    const mockTools = {
      gnu_core: [
        { name: 'GCC', command: 'gcc', installed: true, version: 'gcc 11.4.0', description: 'GNU C Compiler' },
        { name: 'G++', command: 'g++', installed: true, version: 'g++ 11.4.0', description: 'GNU C++ Compiler' },
        { name: 'Make', command: 'make', installed: true, version: 'GNU Make 4.3', description: 'GNU Make build tool' },
        { name: 'GDB', command: 'gdb', installed: false, version: 'Not installed', description: 'GNU Debugger' },
        { name: 'Autoconf', command: 'autoconf', installed: false, version: 'Not installed', description: 'GNU Autoconf' },
        { name: 'Automake', command: 'automake', installed: false, version: 'Not installed', description: 'GNU Automake' },
        { name: 'Bison', command: 'bison', installed: false, version: 'Not installed', description: 'GNU Parser Generator' },
        { name: 'Flex', command: 'flex', installed: false, version: 'Not installed', description: 'Fast Lexical Analyzer' },
      ],
      build_tools: [
        { name: 'CMake', command: 'cmake', installed: true, version: 'cmake 3.22', description: 'Cross-platform build system' },
        { name: 'Ninja', command: 'ninja', installed: false, version: 'Not installed', description: 'Fast build system' },
        { name: 'Meson', command: 'meson', installed: false, version: 'Not installed', description: 'Modern build system' },
      ],
      version_control: [
        { name: 'Git', command: 'git', installed: true, version: 'git 2.34.1', description: 'Distributed version control' },
        { name: 'Git LFS', command: 'git-lfs', installed: false, version: 'Not installed', description: 'Git Large File Storage' },
      ],
      languages: [
        { name: 'Python 3', command: 'python3', installed: true, version: 'Python 3.10.12', description: 'Python programming language' },
        { name: 'Node.js', command: 'node', installed: true, version: 'v18.17.0', description: 'JavaScript runtime' },
        { name: 'Go', command: 'go', installed: false, version: 'Not installed', description: 'Go programming language' },
        { name: 'Rust', command: 'rustc', installed: false, version: 'Not installed', description: 'Rust programming language' },
      ],
      containers: [
        { name: 'Docker', command: 'docker', installed: false, version: 'Not installed', description: 'Container platform' },
        { name: 'Podman', command: 'podman', installed: false, version: 'Not installed', description: 'Daemonless containers' },
      ],
      databases: [
        { name: 'SQLite', command: 'sqlite3', installed: true, version: 'SQLite 3.37.2', description: 'SQLite database' },
        { name: 'PostgreSQL', command: 'psql', installed: false, version: 'Not installed', description: 'PostgreSQL client' },
      ],
      editors: [
        { name: 'Vim', command: 'vim', installed: true, version: 'VIM 8.2', description: 'Vi IMproved' },
        { name: 'Nano', command: 'nano', installed: true, version: 'nano 6.2', description: 'Simple text editor' },
      ],
      networking: [
        { name: 'cURL', command: 'curl', installed: true, version: 'curl 7.81.0', description: 'Command line URL tool' },
        { name: 'Wget', command: 'wget', installed: true, version: 'GNU Wget 1.21.2', description: 'Network downloader' },
      ],
      utilities: [
        { name: 'jq', command: 'jq', installed: false, version: 'Not installed', description: 'JSON processor' },
        { name: 'ripgrep', command: 'rg', installed: false, version: 'Not installed', description: 'Fast grep alternative' },
        { name: 'htop', command: 'htop', installed: true, version: 'htop 3.1.2', description: 'Interactive process viewer' },
        { name: 'tmux', command: 'tmux', installed: false, version: 'Not installed', description: 'Terminal multiplexer' },
      ],
      documentation: [
        { name: 'Man Pages', command: 'man', installed: true, version: 'man-db 2.10.2', description: 'Manual pages' },
        { name: 'Pandoc', command: 'pandoc', installed: false, version: 'Not installed', description: 'Document converter' },
      ],
    };

    setTools(mockTools);
    
    // Calculate stats
    let totalInstalled = 0;
    let totalTools = 0;
    Object.values(mockTools).forEach(category => {
      category.forEach(tool => {
        totalTools++;
        if (tool.installed) totalInstalled++;
      });
    });
    
    setStats({ installed: totalInstalled, total: totalTools });
    setLoading(false);
  }, []);

  const showMessage = (text, type = 'info') => {
    setMessage({ text, type });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleInstall = useCallback((tool) => {
    setInstalling(prev => ({ ...prev, [tool.command]: true }));
    
    // Simulate installation
    setTimeout(() => {
      setInstalling(prev => {
        const newState = { ...prev };
        delete newState[tool.command];
        return newState;
      });
      showMessage(`${tool.name} installed successfully!`, 'success');
      
      // Update tool status
      setTools(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(cat => {
          updated[cat] = updated[cat].map(t => 
            t.command === tool.command ? { ...t, installed: true, version: 'Installed' } : t
          );
        });
        return updated;
      });
    }, 2000);
  }, []);

  const handleInstallBundle = useCallback((bundle) => {
    setInstalling(prev => ({ ...prev, [bundle.id]: true }));
    
    // Simulate bundle installation
    setTimeout(() => {
      setInstalling(prev => {
        const newState = { ...prev };
        delete newState[bundle.id];
        return newState;
      });
      showMessage(`${bundle.name} bundle installed successfully!`, 'success');
    }, 3000);
  }, []);

  const getFilteredTools = () => {
    let allTools = [];
    
    Object.entries(tools).forEach(([category, toolList]) => {
      if (selectedCategory === 'all' || selectedCategory === category) {
        toolList.forEach(tool => {
          allTools.push({ ...tool, category });
        });
      }
    });

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      allTools = allTools.filter(tool => 
        tool.name.toLowerCase().includes(query) ||
        tool.description.toLowerCase().includes(query) ||
        tool.command.toLowerCase().includes(query)
      );
    }

    return allTools;
  };

  const filteredTools = getFilteredTools();

  if (loading) {
    return (
      <div className="dev-tools-loading">
        <div className="loading-spinner">⏳</div>
        <p>Scanning development tools...</p>
      </div>
    );
  }

  return (
    <div className="developer-tools">
      <div className="dev-tools-header">
        <div className="header-info">
          <h2>🛠️ Developer Toolkit</h2>
          <p className="subtitle">
            GNU Tools & Development Environment
            {stats && (
              <span className="stats-badge">
                {stats.installed}/{stats.total} installed
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

      {/* Quick Install Bundles */}
      <div className="bundles-section">
        <h3>📦 Quick Install Bundles</h3>
        <div className="bundles-grid">
          {bundles.map(bundle => (
            <div key={bundle.id} className="bundle-card">
              <span className="bundle-icon">{bundle.icon}</span>
              <div className="bundle-info">
                <span className="bundle-name">{bundle.name}</span>
                <span className="bundle-desc">{bundle.description}</span>
              </div>
              <button
                className={`btn-bundle ${installing[bundle.id] ? 'installing' : ''}`}
                onClick={() => handleInstallBundle(bundle)}
                disabled={installing[bundle.id]}
              >
                {installing[bundle.id] ? 'Installing...' : 'Install'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Search and Filter */}
      <div className="tools-controls">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="category-tabs">
          {categories.map(cat => (
            <button
              key={cat.id}
              className={`category-tab ${selectedCategory === cat.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat.id)}
            >
              <span className="tab-icon">{cat.icon}</span>
              <span className="tab-label">{cat.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tools Grid */}
      <div className="tools-grid">
        {filteredTools.map(tool => (
          <div 
            key={tool.command} 
            className={`tool-card ${tool.installed ? 'installed' : 'not-installed'}`}
          >
            <div className="tool-header">
              <span className="tool-name">{tool.name}</span>
              <span className={`status-badge ${tool.installed ? 'installed' : ''}`}>
                {tool.installed ? '✓' : '○'}
              </span>
            </div>
            
            <div className="tool-body">
              <code className="tool-command">{tool.command}</code>
              <p className="tool-description">{tool.description}</p>
              <span className="tool-version">{tool.version}</span>
            </div>

            <div className="tool-footer">
              <span className="tool-category">{tool.category.replace('_', ' ')}</span>
              {!tool.installed && (
                <button
                  className={`btn-install ${installing[tool.command] ? 'installing' : ''}`}
                  onClick={() => handleInstall(tool)}
                  disabled={installing[tool.command]}
                >
                  {installing[tool.command] ? '⏳' : 'Install'}
                </button>
              )}
            </div>
          </div>
        ))}

        {filteredTools.length === 0 && (
          <div className="no-tools">
            <span className="no-tools-icon">🔍</span>
            <h3>No tools found</h3>
            <p>Try adjusting your search or category filter</p>
          </div>
        )}
      </div>

      <div className="dev-tools-footer">
        <p>
          🐃 Thanks to the <strong>GNU Project</strong> and the 
          <strong> Free Software Foundation</strong> for making development free!
        </p>
      </div>
    </div>
  );
};

export default DeveloperTools;
