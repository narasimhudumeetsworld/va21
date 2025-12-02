import React, { useState, useEffect, useCallback } from 'react';
import './ResearchCommandCenter.css';
import io from 'socket.io-client';

// Graph visualization component
const KnowledgeGraph = ({ nodes, edges, onNodeClick }) => {
  return (
    <div className="knowledge-graph">
      <div className="graph-header">
        <h3>Knowledge Graph</h3>
        <span className="node-count">{nodes.length} nodes</span>
      </div>
      <div className="graph-container">
        {nodes.length === 0 ? (
          <div className="empty-graph">
            <span>📊</span>
            <p>No knowledge graph data yet</p>
            <p className="hint">Start researching to build your knowledge base</p>
          </div>
        ) : (
          <div className="graph-nodes">
            {nodes.map((node, index) => (
              <div 
                key={node.id}
                className="graph-node"
                onClick={() => onNodeClick(node)}
                style={{
                  '--delay': `${index * 0.1}s`
                }}
              >
                <span className="node-icon">📄</span>
                <span className="node-title">{node.title}</span>
                <div className="node-tags">
                  {(node.tags || []).slice(0, 3).map((tag, i) => (
                    <span key={i} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Research session component
const ResearchSession = ({ session, onSelect }) => {
  return (
    <div className="research-session" onClick={() => onSelect(session)}>
      <div className="session-header">
        <span className="session-icon">🔬</span>
        <span className="session-title">{session.title}</span>
      </div>
      <div className="session-meta">
        <span className="session-date">{new Date(session.date).toLocaleDateString()}</span>
        <span className="session-type">{session.type}</span>
      </div>
    </div>
  );
};

// Note viewer/editor component
const NoteViewer = ({ note, onClose }) => {
  if (!note) return null;

  return (
    <div className="note-viewer">
      <div className="note-header">
        <h3>{note.title}</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      <div className="note-content">
        <pre>{note.content || 'No content'}</pre>
      </div>
      <div className="note-footer">
        <div className="note-tags">
          {(note.tags || []).map((tag, i) => (
            <span key={i} className="tag">{tag}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

// Memory panel component
const MemoryPanel = ({ memories, onMemoryClick }) => {
  return (
    <div className="memory-panel">
      <div className="panel-header">
        <h3>🧠 LLM Memory</h3>
      </div>
      <div className="memory-list">
        {memories.length === 0 ? (
          <div className="empty-memory">
            <p>No memories stored yet</p>
          </div>
        ) : (
          memories.map((memory, index) => (
            <div 
              key={index} 
              className="memory-item"
              onClick={() => onMemoryClick(memory)}
            >
              <span className="memory-context">{memory.context?.substring(0, 100)}...</span>
              <span className="memory-date">
                {new Date(memory.timestamp).toLocaleString()}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Quick actions panel
const QuickActions = ({ onAction }) => {
  const actions = [
    { id: 'new_research', icon: '🔬', label: 'New Research' },
    { id: 'new_note', icon: '📝', label: 'New Note' },
    { id: 'search', icon: '🔍', label: 'Search Vault' },
    { id: 'export', icon: '📤', label: 'Export Data' },
    { id: 'sync', icon: '🔄', label: 'Sync Graph' },
  ];

  return (
    <div className="quick-actions">
      {actions.map(action => (
        <button 
          key={action.id}
          className="action-btn"
          onClick={() => onAction(action.id)}
        >
          <span className="action-icon">{action.icon}</span>
          <span className="action-label">{action.label}</span>
        </button>
      ))}
    </div>
  );
};

function ResearchCommandCenter() {
  const [socket, setSocket] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [sessions, setSessions] = useState([]);
  const [memories, setMemories] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showNewResearchModal, setShowNewResearchModal] = useState(false);
  const [newResearch, setNewResearch] = useState({ title: '', objective: '', topics: '' });

  useEffect(() => {
    const newSocket = io('/research');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to research server');
      newSocket.emit('get_graph_data');
      newSocket.emit('get_sessions');
      newSocket.emit('get_memories');
    });

    newSocket.on('graph_data', (data) => {
      setGraphData(data);
    });

    newSocket.on('sessions_list', (data) => {
      setSessions(data);
    });

    newSocket.on('memories_list', (data) => {
      setMemories(data);
    });

    newSocket.on('search_results', (data) => {
      setSearchResults(data);
    });

    newSocket.on('note_data', (data) => {
      setSelectedNote(data);
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const handleNodeClick = useCallback((node) => {
    if (socket) {
      socket.emit('get_note', { path: node.path });
    }
  }, [socket]);

  const handleSearch = useCallback((e) => {
    e.preventDefault();
    if (socket && searchQuery.trim()) {
      socket.emit('search_vault', { query: searchQuery });
    }
  }, [socket, searchQuery]);

  const handleAction = useCallback((actionId) => {
    switch (actionId) {
      case 'new_research':
        setShowNewResearchModal(true);
        break;
      case 'new_note':
        // Open note creation
        break;
      case 'search':
        // Focus search
        break;
      case 'export':
        if (socket) {
          socket.emit('export_data');
        }
        break;
      case 'sync':
        if (socket) {
          socket.emit('get_graph_data');
        }
        break;
      default:
        break;
    }
  }, [socket]);

  const handleCreateResearch = useCallback((e) => {
    e.preventDefault();
    if (socket && newResearch.title.trim()) {
      socket.emit('create_research_session', {
        title: newResearch.title,
        objective: newResearch.objective,
        topics: newResearch.topics.split(',').map(t => t.trim()).filter(t => t)
      });
      setShowNewResearchModal(false);
      setNewResearch({ title: '', objective: '', topics: '' });
    }
  }, [socket, newResearch]);

  return (
    <div className="research-command-center">
      <div className="rcc-header">
        <h2>🔬 Research Command Center</h2>
        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search knowledge base..."
            className="search-input"
          />
          <button type="submit" className="search-btn">🔍</button>
        </form>
      </div>

      <QuickActions onAction={handleAction} />

      <div className="rcc-main">
        <div className="rcc-sidebar">
          <div className="sessions-panel">
            <h3>📚 Research Sessions</h3>
            <div className="sessions-list">
              {sessions.map((session, index) => (
                <ResearchSession 
                  key={index}
                  session={session}
                  onSelect={(s) => socket?.emit('get_note', { path: s.path })}
                />
              ))}
            </div>
          </div>
          <MemoryPanel 
            memories={memories}
            onMemoryClick={(m) => setSelectedNote(m)}
          />
        </div>

        <div className="rcc-content">
          {selectedNote ? (
            <NoteViewer 
              note={selectedNote}
              onClose={() => setSelectedNote(null)}
            />
          ) : searchResults.length > 0 ? (
            <div className="search-results">
              <h3>Search Results ({searchResults.length})</h3>
              <div className="results-list">
                {searchResults.map((result, index) => (
                  <div 
                    key={index}
                    className="result-item"
                    onClick={() => socket?.emit('get_note', { path: result.path })}
                  >
                    <span className="result-title">{result.title}</span>
                    <span className="result-type">{result.type}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <KnowledgeGraph 
              nodes={graphData.nodes}
              edges={graphData.edges}
              onNodeClick={handleNodeClick}
            />
          )}
        </div>
      </div>

      {showNewResearchModal && (
        <div className="modal-overlay" onClick={() => setShowNewResearchModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>New Research Session</h3>
            <form onSubmit={handleCreateResearch}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={newResearch.title}
                  onChange={e => setNewResearch({...newResearch, title: e.target.value})}
                  placeholder="Research session title..."
                  required
                />
              </div>
              <div className="form-group">
                <label>Objective</label>
                <textarea
                  value={newResearch.objective}
                  onChange={e => setNewResearch({...newResearch, objective: e.target.value})}
                  placeholder="What are you trying to learn or discover?"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Topics (comma-separated)</label>
                <input
                  type="text"
                  value={newResearch.topics}
                  onChange={e => setNewResearch({...newResearch, topics: e.target.value})}
                  placeholder="ai, security, machine-learning"
                />
              </div>
              <div className="form-actions">
                <button type="button" onClick={() => setShowNewResearchModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary">
                  Create Session
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResearchCommandCenter;
