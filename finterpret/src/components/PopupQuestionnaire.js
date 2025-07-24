import React, { useState } from 'react';
import './PopupQuestionnaire.css';

const questions = [
  {
    question: "What is your approximate monthly income?",
    options: [
      "Less than $500",
      "$500 - $2,000",
      "$2,000 - $5,000",
      "$5,000 - $10,000",
      "Over $10,000"
    ]
  },
  {
    question: "How much do you typically spend per month?",
    options: [
      "Less than $300",
      "$300 - $1,500",
      "$1,500 - $3,000",
      "$3,000 - $6,000",
      "Over $6,000"
    ]
  },
  {
    question: "Do you have any existing debts or loans?",
    options: [
      "No debt",
      "Some student/education debt",
      "Some credit card debt",
      "Significant mortgage or car loan",
      "Heavy debt across multiple sources"
    ]
  },
  {
    question: "What are your short-term financial goals?",
    options: [
      "Save for an emergency fund",
      "Save for a major purchase",
      "Pay off debt",
      "Invest and grow wealth",
      "Improve budgeting and control spending"
    ]
  },
  {
    question: "How would you describe your risk appetite?",
    options: [
      "Very conservative",
      "Somewhat conservative",
      "Balanced",
      "Aggressive",
      "Very aggressive"
    ]
  }
];

export default function PopupQuestionnaire({ onClose }) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);

  const handleSelect = (option) => {
    const updatedAnswers = [...answers];
    updatedAnswers[currentQuestion] = option;
    setAnswers(updatedAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      console.log("User Responses:", updatedAnswers);
      // You can send answers to backend here
      onClose();
    }
  };

  const q = questions[currentQuestion];

  return (
    <div className="popup-overlay">
      <div className="popup-content">
        <button className="close-button" onClick={onClose}>×</button>
        <h2>💰 Financial Check-In</h2>
        <p>{q.question}</p>
        <div className="options">
          {q.options.map((opt, index) => (
            <button key={index} onClick={() => handleSelect(opt)}>
              {opt}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

}
