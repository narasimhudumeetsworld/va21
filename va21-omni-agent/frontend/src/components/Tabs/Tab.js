import React from 'react';
import './Tab.css';

const Tab = ({ tab, isSelected, onSelect, onClose }) => {
  const handleClose = (e) => {
    e.stopPropagation(); // Prevent the onSelect event from firing
    onClose();
  };

  return (
    <div className={`tab ${isSelected ? 'active' : ''}`} onClick={onSelect}>
      {/* Add a placeholder for a favicon later */}
      <div className="tab-icon"></div>
      <span className="tab-title">{tab.title || 'New Tab'}</span>
      <button className="close-tab-button" onClick={handleClose}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>
    </div>
  );
};

export default Tab;
