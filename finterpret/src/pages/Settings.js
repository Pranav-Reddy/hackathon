import React, { useState } from 'react';
import './Settings.css'; // Import custom styles for Settings page
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserCircle } from '@fortawesome/free-solid-svg-icons';  // User icon from Font Awesome


const Settings = () => {
  // State variables
  const [username, setUsername] = useState('andrewgmartin1999'); // Mocked username
  const [textSize, setTextSize] = useState('medium'); // Medium by default
  const [financialGoal, setFinancialGoal] = useState('Savings');

  // Handle text size change
  const handleTextSizeChange = (event) => {
    setTextSize(event.target.value);
  };

  // Handle financial goal change
  const handleGoalChange = (event) => {
    setFinancialGoal(event.target.value);
  };

  return (
    <div className={`settings-container ${textSize}`}>
      {/* Profile Icon */}
      <div className="profile-icon">
        <FontAwesomeIcon icon={faUserCircle} size="4x" />
      </div>

      <h1>Settings</h1>

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

      <div className="setting-item">
        <label>Financial Goal</label>
        <input
          type="text"
          value={financialGoal}
          onChange={handleGoalChange}
          placeholder="Enter your new goal"
        />
      </div>
    </div>
  );
};

export default Settings;

