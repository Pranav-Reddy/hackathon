import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale } from 'chart.js';

// Import custom CSS for Goals page
import './Goals.css'; // Make sure the path is correct

// Registering the required Chart.js components
ChartJS.register(Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale);

const Goals = () => {
  // Sample financial data
  const data = {
    labels: ['Savings', 'Groceries', 'Gas', 'Entertainment', 'Rent'], // Sections for the pie chart
    datasets: [
      {
        label: 'Financial Goals',
        data: [30, 20, 10, 15, 25], // Percentages of each section
        backgroundColor: [
          '#36A2EB', // Savings
          '#FF6384', // Groceries
          '#FFCD56', // Gas
          '#4BC0C0', // Entertainment
          '#FF9F40', // Rent
        ],
        borderColor: '#fff',
        borderWidth: 1,
      },
    ],
  };

  // Options for customizing the chart size
  const options = {
    responsive: true,
    maintainAspectRatio: false, // Allow resizing through CSS
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(tooltipItem) {
            return tooltipItem.label + ': ' + tooltipItem.raw + '%';
          },
        },
      },
    },
    aspectRatio: 1,  // Make the chart square (1:1 ratio)
  };

  return (
    <div className="page-container">
    <div className="goals-container">
      <h1>Your Financial Goals</h1>
      <p>Here's a breakdown of people's typical financial goals and their allocation.</p>

      {/* Pie Chart */}
      <div className="chart-container">
        <Pie data={data} options={options} />
      </div>

      <div className="goal-info">
        <h2>Goal Details</h2>
        <p>
          Financial goals help individuals manage their income and plan for future needs. The sections above
          represent how people typically allocate their finances across different categories. Adjustments can
          be made based on personal priorities.

	  Here's how yours compares:
        </p>
      </div>
    </div>
    </div>
  );
};

export default Goals;

