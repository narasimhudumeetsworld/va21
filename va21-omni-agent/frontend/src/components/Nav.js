import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Nav.css';

function Nav() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Chat', icon: '💬' },
    { path: '/research', label: 'Research', icon: '🔬' },
    { path: '/terminals', label: 'Terminals', icon: '📟' },
    { path: '/documents', label: 'Documents', icon: '📄' },
    { path: '/bookmarks', label: 'Bookmarks', icon: '🔖' },
    { path: '/backups', label: 'Backups', icon: '💾' },
    { path: '/stats', label: 'Stats', icon: '📊' },
    { path: '/workflows', label: 'Workflows', icon: '⚙️' },
    { path: '/shortcuts', label: 'Shortcuts', icon: '⌨️' },
    { path: '/settings', label: 'Settings', icon: '🔧' },
  ];
  
  return (
    <nav className="nav">
      <div className="nav-header">
        <span className="nav-logo">🛡️</span>
        <span className="nav-title">VA21</span>
      </div>
      <ul>
        {navItems.map(item => (
          <li key={item.path}>
            <Link 
              to={item.path}
              className={location.pathname === item.path ? 'active' : ''}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Nav;
