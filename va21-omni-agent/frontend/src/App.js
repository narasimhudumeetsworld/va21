import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import './App.css';
import TabBar from './components/Tabs/TabBar';
import AddressBar from './components/Browser/AddressBar';
import SidePanel from './components/SidePanel/SidePanel';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [isSidePanelOpen, setSidePanelOpen] = useState(false);
  const [tabs, setTabs] = useState([]);
  const [activeTabId, setActiveTabId] = useState(null);

  // Initialize with a single tab on mount
  useEffect(() => {
    const firstTabId = uuidv4();
    const newTab = { id: firstTabId, title: 'New Tab', url: '' };
    setTabs([newTab]);
    setActiveTabId(firstTabId);
    window.electronAPI?.newTab({ id: firstTabId, url: 'app://new-tab' });
  }, []);

  const handleNewTab = useCallback(() => {
    const newTabId = uuidv4();
    const newTab = { id: newTabId, title: 'New Tab', url: '' };
    setTabs(prevTabs => [...prevTabs, newTab]);
    setActiveTabId(newTabId);
    window.electronAPI?.newTab({ id: newTabId, url: 'app://new-tab' });
  }, []);

  const handleSelectTab = useCallback((tabId) => {
    setActiveTabId(tabId);
    window.electronAPI?.selectTab(tabId);
  }, []);

  const handleCloseTab = useCallback((tabId) => {
    window.electronAPI?.closeTab(tabId);
    setTabs(prevTabs => {
      const remainingTabs = prevTabs.filter(t => t.id !== tabId);
      if (remainingTabs.length === 0) {
        // If no tabs are left, create a new one
        handleNewTab();
      } else if (activeTabId === tabId) {
        // If the closed tab was active, select the last tab in the list
        const newActiveTab = remainingTabs[remainingTabs.length - 1];
        setActiveTabId(newActiveTab.id);
        window.electronAPI?.selectTab(newActiveTab.id);
      }
      return remainingTabs;
    });
  }, [activeTabId, handleNewTab]);

  const toggleSidePanel = () => {
    setSidePanelOpen(!isSidePanelOpen);
    window.electronAPI?.toggleSidePanel(!isSidePanelOpen);
  };

  // Listen for updates from the main process
  useEffect(() => {
    const unregister = window.electronAPI?.onTabUpdate((updatedTab) => {
      setTabs(prevTabs =>
        prevTabs.map(tab =>
          tab.id === updatedTab.id ? { ...tab, ...updatedTab } : tab
        )
      );
    });

    return () => unregister && unregister();
  }, []);

  return (
    <Router>
      <div className="App">
        <div className="browser-chrome">
          <TabBar
            tabs={tabs}
            activeTabId={activeTabId}
            onSelectTab={handleSelectTab}
            onCloseTab={handleCloseTab}
            onNewTab={handleNewTab}
          />
          <AddressBar
            onToggleSidePanel={toggleSidePanel}
            activeTab={tabs.find(t => t.id === activeTabId)}
          />
        </div>
        <SidePanel isOpen={isSidePanelOpen} />
        {/* The main BrowserView is managed by Electron and placed behind this window */}
      </div>
    </Router>
  );
}

export default App;
