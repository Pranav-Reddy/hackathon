import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement, CategoryScale, LinearScale } from 'chart.js';

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

  return (
    <div className="goals-container">
      <h1>People's Financial Goals</h1>
      <p>Here's a breakdown of people's typical financial goals and their allocation.</p>

      {/* Pie Chart */}
      <div className="chart-container">
        <Pie data={data} />
      </div>

      <div className="goal-info">
        <h2>Goal Details</h2>
        <p>
          Financial goals help individuals manage their income and plan for future needs. The sections above
          represent how people typically allocate their finances across different categories. Adjustments can
          be made based on personal priorities.
        </p>
      </div>
    </div>
  );
};

export default Goals;

