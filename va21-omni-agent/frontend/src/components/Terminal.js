import React, { useRef, useEffect, useState } from 'react';
import { XTerm } from 'xterm-react';
import 'xterm/css/xterm.css';
import './Terminal.css';
import io from 'socket.io-client';

const socket = io('/terminal');

function Terminal() {
  const xtermRef = useRef(null);
  const [agentMode, setAgentMode] = useState(false);
  const [inputBuffer, setInputBuffer] = useState('');

  useEffect(() => {
    if (xtermRef.current) {
      const term = xtermRef.current.terminal;

      socket.on('terminal_out', (data) => {
        term.write(data.output);
      });

      const onDataDisposable = term.onData((data) => {
        if (agentMode) {
          const code = data.charCodeAt(0);
          if (code === 13) { // Enter key
            term.write('\r\n');
            socket.emit('agent_command', inputBuffer);
            setInputBuffer('');
          } else if (code === 127) { // Backspace
            if (inputBuffer.length > 0) {
              term.write('\b \b');
              setInputBuffer(inputBuffer.slice(0, -1));
            }
          } else if (code >= 32) { // Printable characters
            term.write(data);
            setInputBuffer(inputBuffer + data);
          }
        } else {
          socket.emit('terminal_in', data);
        }
      });

      return () => {
        socket.off('terminal_out');
        onDataDisposable.dispose();
      };
    }
  }, [agentMode, inputBuffer]);

  return (
    <div className="terminal-container">
      <div className="terminal-controls">
        <label>
          <input
            type="checkbox"
            checked={agentMode}
            onChange={() => setAgentMode(!agentMode)}
          />
          Agent Mode
        </label>
      </div>
      <XTerm ref={xtermRef} />
    </div>
  );
}

export default Terminal;
