import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PopupQuestionnaire from './components/PopupQuestionnaire';

import Home from './pages/Home';
import Goals from './pages/Goals';
import Advisory from './pages/Advisory';
import Settings from './pages/Settings';

import './App.css';

function App() {
  const [showPopup, setShowPopup] = useState(true);

  const handleClosePopup = () => setShowPopup(false);

  return (
    <Router>
      <div className="App">
        {showPopup && <PopupQuestionnaire onClose={handleClosePopup} />}

        {!showPopup && (
          <>
            <nav className="navbar">
              <Link to="/">Home</Link>
              <Link to="/goals">Goals</Link>
              <Link to="/advisory">Advisory</Link>
              <Link to="/settings">Settings</Link>
            </nav>

            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/goals" element={<Goals />} />
              <Route path="/advisory" element={<Advisory />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </>
        )}
      </div>
    </Router>
  );
}

export default App;
