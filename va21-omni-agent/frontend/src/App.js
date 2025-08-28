import React, { useState } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import './App.css';
import TitleBar from './components/Browser/TitleBar';
import AddressBar from './components/Browser/AddressBar';
import SidePanel from './components/SidePanel/SidePanel';

function App() {
  const [isSidePanelOpen, setSidePanelOpen] = useState(false);

  const toggleSidePanel = () => {
    setSidePanelOpen(!isSidePanelOpen);
    // Notify the main process that the panel state has changed
    if (window.electronAPI && window.electronAPI.toggleSidePanel) {
      window.electronAPI.toggleSidePanel(!isSidePanelOpen);
    }
  };

  return (
    <Router>
      <div className="App">
        <TitleBar />
        <AddressBar onToggleSidePanel={toggleSidePanel} />
        <SidePanel isOpen={isSidePanelOpen} />
        {/* The main browser view will be managed by Electron and will occupy
            the space not taken by the side panel. */}
      </div>
    </Router>
  );
}

export default App;
