import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Nav from './components/Nav';
import Chat from './components/Chat';
import Settings from './components/Settings';
import Terminal from './components/Terminal';

function App() {
  return (
    <Router>
      <div className="App">
        <Nav />
        <main>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/terminal" element={<Terminal />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
