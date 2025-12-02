import React from 'react';
import { Link } from 'react-router-dom';
import './Nav.css';

function Nav() {
  return (
    <nav className="nav">
      <ul>
        <li>
          <Link to="/">Chat</Link>
        </li>
        <li>
          <Link to="/research">Research</Link>
        </li>
        <li>
          <Link to="/terminals">Terminals</Link>
        </li>
        <li>
          <Link to="/terminal">Terminal</Link>
        </li>
        <li>
          <Link to="/documents">Documents</Link>
        </li>
        <li>
          <Link to="/workflows">Workflows</Link>
        </li>
        <li>
          <Link to="/settings">Settings</Link>
        </li>
      </ul>
    </nav>
  );
}

export default Nav;
