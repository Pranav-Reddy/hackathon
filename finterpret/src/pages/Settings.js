import React, { useState } from 'react';
// import './Settings.css'; // Import custom styles for Settings page
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserCircle } from '@fortawesome/free-solid-svg-icons';  // User icon from Font Awesome

const Settings = () => {
  // State variables
  const [username, setUsername] = useState('Andrewtootru'); // Mocked username
  const [textSize, setTextSize] = useState('medium'); // Medium by default
  const [financialGoal, setFinancialGoal] = useState('Savings');

  // Handle text size change
  const handleTextSizeChange = (event) => {
    setTextSize(event.target.value);
  };

  // Handle financial goal change
  const handleGoalChange = () => {
    // Just a placeholder for button action
    alert('Change goals functionality is not implemented yet.');
  };

  return (
    <div className="page-container">
    <div className={`settings-container ${textSize}`}>
      {/* Profile Icon */}
      <div className="profile-icon">
        <FontAwesomeIcon icon={faUserCircle} size="4x" />
      </div>

      <h1>Settings</h1>

      <div className="settings-row">
        <div className="setting-item">
          <label>Username</label>
          <p>{username}</p>
        </div>

        <div className="setting-item">
          <label>Text Size</label>
          <select value={textSize} onChange={handleTextSizeChange}>
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>
      </div>

      {/* Button to change financial goal */}
      <div className="setting-item">
        <button className="goal-button" onClick={handleGoalChange}>Change Goals</button>
      </div>
    </div>
    </div>
  );
};

export default Settings;

