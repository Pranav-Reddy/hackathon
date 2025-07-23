import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PopupQuestionnaire from './components/PopupQuestionnaire';
import { FaHome, FaBullseye, FaUserFriends, FaCog } from 'react-icons/fa';

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
            <nav className="bottom-tab-nav">
              <Link to="/" className="tab-icon">
                <FaHome size={24} />
              </Link>
              <Link to="/goals" className="tab-icon">
                <FaBullseye size={24} />
              </Link>
              <Link to="/advisory" className="tab-icon">
                <FaUserFriends size={24} />
              </Link>
              <Link to="/settings" className="tab-icon">
                <FaCog size={24} />
              </Link>
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
