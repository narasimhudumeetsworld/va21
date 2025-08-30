import React from 'react';
import Tab from './Tab';
import './TabBar.css';

const TabBar = ({ tabs, onSelectTab, onCloseTab, onNewTab, activeTabId }) => {
  return (
    <div className="tab-bar">
      {tabs.map(tab => (
        <Tab
          key={tab.id}
          tab={tab}
          isSelected={tab.id === activeTabId}
          onSelect={() => onSelectTab(tab.id)}
          onClose={() => onCloseTab(tab.id)}
        />
      ))}
      <button className="new-tab-button" onClick={onNewTab}>+</button>
    </div>
  );
};

export default TabBar;
