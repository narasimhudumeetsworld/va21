import React from 'react';
import './SidePanel.css';
import { Routes, Route } from 'react-router-dom';
import Nav from '../Nav';
import Chat from '../Chat';
import Settings from '../Settings';
import Terminal from '../Terminal';
import TilingTerminals from '../TilingTerminals';
import Documents from '../Documents';
import Workflows from '../Workflows';
import ResearchCommandCenter from '../ResearchCommandCenter';
import Bookmarks from '../Bookmarks';
import BackupManager from '../BackupManager';
import SystemStats from '../SystemStats';
import KeyboardShortcuts from '../KeyboardShortcuts';
import AppCenter from '../AppCenter';
import DeveloperTools from '../DeveloperTools';
import CodeHistory from '../CodeHistory';

const SidePanel = ({ isOpen }) => {
  return (
    <div className={`side-panel ${isOpen ? 'open' : ''}`}>
      <div className="side-panel-content">
        <Nav />
        <main>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/research" element={<ResearchCommandCenter />} />
            <Route path="/terminals" element={<TilingTerminals />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/terminal" element={<Terminal />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/workflows" element={<Workflows />} />
            <Route path="/bookmarks" element={<Bookmarks />} />
            <Route path="/backups" element={<BackupManager />} />
            <Route path="/stats" element={<SystemStats />} />
            <Route path="/shortcuts" element={<KeyboardShortcuts />} />
            <Route path="/apps" element={<AppCenter />} />
            <Route path="/devtools" element={<DeveloperTools />} />
            <Route path="/code-history" element={<CodeHistory />} />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default SidePanel;
