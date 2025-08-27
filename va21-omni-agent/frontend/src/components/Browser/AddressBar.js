import React, { useState } from 'react';
import './AddressBar.css';

const AddressBar = ({ onToggleSidePanel }) => {
  const [url, setUrl] = useState('https://www.google.com');

  const handleNavigate = () => {
    // Basic URL validation
    let finalUrl = url;
    if (!finalUrl.startsWith('http://') && !finalUrl.startsWith('https://')) {
      finalUrl = 'http://' + finalUrl;
    }
    window.electronAPI.navigateTo(finalUrl);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleNavigate();
    }
  };

  return (
    <div className="address-bar">
      <button onClick={() => window.electronAPI.navigateBack()} className="nav-button">{'<'}</button>
      <button onClick={() => window.electronAPI.navigateForward()} className="nav-button">{'>'}</button>
      <button onClick={() => window.electronAPI.navigateReload()} className="nav-button">{'↻'}</button>
      <input
        type="text"
        className="address-input"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button onClick={onToggleSidePanel} className="agent-button">VA</button>
    </div>
  );
};

export default AddressBar;
