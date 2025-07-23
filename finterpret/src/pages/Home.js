import { useState } from "react";

export default function Home() {
  const [spending, setSpending] = useState(0);
  const [goal, setGoal] = useState(1000);
  const [showDialog, setShowDialog] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">FinanceCoach</h1>
        <div className="space-x-4">
          <button
            onClick={() => setShowDialog(true)}
            className="border px-4 py-2 rounded hover:bg-gray-100"
          >
            Add Today's Spending
          </button>
          <button className="text-gray-700 hover:underline">Goals</button>
          <button className="text-gray-700 hover:underline">Advisor</button>
          <button className="text-gray-700 hover:underline">Settings</button>
        </div>
      </nav>

      {/* Modal Dialog for Spending Entry */}
      {showDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-96">
            <h2 className="text-lg font-semibold mb-4">Enter Spending</h2>
            <input
              type="number"
              placeholder="Amount"
              className="border w-full p-2 rounded"
              onChange={(e) => setSpending(Number(e.target.value))}
            />
            <div className="flex justify-end mt-4 space-x-2">
              <button
                onClick={() => setShowDialog(false)}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  alert("Spending saved!");
                  setShowDialog(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Goal Progress Dashboard */}
      <main className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Your Progress</h2>
        <div className="bg-white shadow rounded p-6 max-w-md mx-auto">
          <p className="text-lg mb-2">Goal: ${goal}</p>
          <p className="text-lg mb-4">Spent: ${spending}</p>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-blue-600 h-4 rounded-full transition-all duration-300"
              style={{ width: `${Math.min((spending / goal) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      </main>
    </div>
  );
}
