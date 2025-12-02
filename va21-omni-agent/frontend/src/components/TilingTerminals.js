import React, { useState, useCallback, useEffect } from 'react';
import './TilingTerminals.css';
import io from 'socket.io-client';

// Terminal component for each pane
const TerminalPane = ({ id, socket, isActive, onActivate }) => {
  const [output, setOutput] = useState('');
  const [inputValue, setInputValue] = useState('');
  const terminalRef = React.useRef(null);

  useEffect(() => {
    if (socket) {
      const handleOutput = (data) => {
        if (data.terminal_id === id) {
          setOutput(prev => prev + data.output);
        }
      };

      socket.on('terminal_output', handleOutput);

      return () => {
        socket.off('terminal_output', handleOutput);
      };
    }
  }, [socket, id]);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (socket && inputValue.trim()) {
      socket.emit('terminal_input', { terminal_id: id, input: inputValue + '\n' });
      setInputValue('');
    }
  };

  return (
    <div 
      className={`terminal-pane ${isActive ? 'active' : ''}`}
      onClick={onActivate}
    >
      <div className="terminal-header">
        <span className="terminal-title">Terminal {id}</span>
        <div className="terminal-status">
          <span className="status-dot"></span>
        </div>
      </div>
      <div className="terminal-output" ref={terminalRef}>
        <pre>{output}</pre>
      </div>
      <form className="terminal-input-form" onSubmit={handleSubmit}>
        <span className="prompt">$</span>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter command..."
          className="terminal-input"
        />
      </form>
    </div>
  );
};

// Layout configurations
const LAYOUTS = {
  single: { rows: 1, cols: 1 },
  splitH: { rows: 1, cols: 2 },
  splitV: { rows: 2, cols: 1 },
  quad: { rows: 2, cols: 2 },
  triple: { rows: 1, cols: 3 },
  six: { rows: 2, cols: 3 },
};

function TilingTerminals() {
  const [layout, setLayout] = useState('quad');
  const [terminals, setTerminals] = useState([]);
  const [activeTerminal, setActiveTerminal] = useState(null);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io('/terminals');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to terminal server');
    });

    newSocket.on('terminal_created', (data) => {
      setTerminals(prev => [...prev, data]);
    });

    newSocket.on('terminal_destroyed', (data) => {
      setTerminals(prev => prev.filter(t => t.id !== data.terminal_id));
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  // Calculate number of panes based on layout
  const getLayoutInfo = useCallback(() => {
    return LAYOUTS[layout] || LAYOUTS.quad;
  }, [layout]);

  const createTerminal = useCallback(() => {
    if (socket) {
      socket.emit('create_terminal', { 
        name: `Terminal-${terminals.length + 1}`,
        sandbox_level: 'standard'
      });
    }
  }, [socket, terminals.length]);

  const destroyTerminal = useCallback((id) => {
    if (socket) {
      socket.emit('destroy_terminal', { terminal_id: id });
    }
  }, [socket]);

  const layoutInfo = getLayoutInfo();
  const totalPanes = layoutInfo.rows * layoutInfo.cols;

  // Ensure we have enough terminals - with debouncing to prevent race conditions
  useEffect(() => {
    const needed = totalPanes - terminals.length;
    if (needed > 0 && needed <= 6) {  // Safety limit to prevent infinite creation
      // Create only one terminal at a time to prevent race conditions
      createTerminal();
    }
  }, [totalPanes, terminals.length, createTerminal]);

  return (
    <div className="tiling-terminals">
      <div className="tiling-toolbar">
        <div className="layout-buttons">
          <button 
            className={layout === 'single' ? 'active' : ''}
            onClick={() => setLayout('single')}
            title="Single pane"
          >
            ▢
          </button>
          <button 
            className={layout === 'splitH' ? 'active' : ''}
            onClick={() => setLayout('splitH')}
            title="Horizontal split"
          >
            ⊞
          </button>
          <button 
            className={layout === 'splitV' ? 'active' : ''}
            onClick={() => setLayout('splitV')}
            title="Vertical split"
          >
            ⊟
          </button>
          <button 
            className={layout === 'quad' ? 'active' : ''}
            onClick={() => setLayout('quad')}
            title="Quad panes"
          >
            ⊠
          </button>
          <button 
            className={layout === 'triple' ? 'active' : ''}
            onClick={() => setLayout('triple')}
            title="Triple panes"
          >
            ⋮⋮⋮
          </button>
          <button 
            className={layout === 'six' ? 'active' : ''}
            onClick={() => setLayout('six')}
            title="Six panes"
          >
            ⋯⋯
          </button>
        </div>
        <div className="terminal-actions">
          <button onClick={createTerminal} className="add-terminal">
            + New Terminal
          </button>
        </div>
      </div>
      <div 
        className="terminal-grid"
        style={{
          gridTemplateRows: `repeat(${layoutInfo.rows}, 1fr)`,
          gridTemplateColumns: `repeat(${layoutInfo.cols}, 1fr)`
        }}
      >
        {terminals.slice(0, totalPanes).map((terminal, index) => (
          <TerminalPane
            key={terminal.id}
            id={terminal.id}
            socket={socket}
            isActive={activeTerminal === terminal.id}
            onActivate={() => setActiveTerminal(terminal.id)}
          />
        ))}
      </div>
    </div>
  );
}

export default TilingTerminals;
