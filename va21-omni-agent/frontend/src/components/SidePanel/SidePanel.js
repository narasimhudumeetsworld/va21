import React from 'react';
import './SidePanel.css';
import { Routes, Route } from 'react-router-dom';
import Nav from '../Nav';
import Chat from '../Chat';
import Settings from '../Settings';
import Terminal from '../Terminal';
import Documents from '../Documents';
import Workflows from '../Workflows';

const SidePanel = ({ isOpen }) => {
  return (
    <div className={`side-panel ${isOpen ? 'open' : ''}`}>
      <div className="side-panel-content">
        <Nav />
        <main>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/terminal" element={<Terminal />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/workflows" element={<Workflows />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default SidePanel;
