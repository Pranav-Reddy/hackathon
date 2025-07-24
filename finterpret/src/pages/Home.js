import { useState } from "react";
import { Button } from "../homepage-components/Button.js";
import { Card, CardContent } from "../homepage-components/Card.js";
import { Dialog } from "../homepage-components/Dialog.js";
import { Input } from "../homepage-components/Input.js";
import { Progress } from "../homepage-components/Progress.js";


import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area
} from "recharts";

export default function Home() {
  const [spending, setSpending] = useState(0);
  const [goal, setGoal] = useState(1000);
  const [spendingData, setSpendingData] = useState([]);
  const [selectedSpending, setSelectedSpending] = useState([]);
  const [timeframe, setTimeframe] = useState("day");
  const [showDetails, setShowDetails] = useState(false);

  const handleAddSpending = () => {
    const now = new Date();
    const label = now.toLocaleString();
    const newEntry = { time: label, amount: spending };
    setSpendingData([...spendingData, newEntry]);
    setSelectedSpending([...selectedSpending, true]);
    alert("Spending saved!");
  };

  const handleToggleSpending = (index) => {
    const updated = [...selectedSpending];
    updated[index] = !updated[index];
    setSelectedSpending(updated);
  };

  const handleDeleteSpending = (index) => {
    const updatedData = spendingData.filter((_, i) => i !== index);
    const updatedSelection = selectedSpending.filter((_, i) => i !== index);
    setSpendingData(updatedData);
    setSelectedSpending(updatedSelection);
  };

  const handleSelectAll = () => {
    setSelectedSpending(new Array(spendingData.length).fill(true));
  };

  const getFilteredData = () => {
    const includedData = spendingData
      .map((d, i) => ({ ...d, included: selectedSpending[i] }))
      .filter((d) => d.included);

    if (includedData.length <= 1) return includedData.map((d) => ({ ...d, cumulative: d.amount }));

    const now = new Date();
    const dayMs = 24 * 60 * 60 * 1000;
    const weekMs = 7 * dayMs;
    const monthMs = 30 * dayMs;

    let cutoff;
    if (timeframe === "day") cutoff = now.getTime() - dayMs;
    else if (timeframe === "week") cutoff = now.getTime() - weekMs;
    else cutoff = now.getTime() - monthMs;

    const data = includedData.filter((d) => new Date(d.time).getTime() >= cutoff);
    let cumulative = 0;
    return data.map((d) => {
      cumulative += d.amount;
      return { ...d, cumulative };
    });
  };

  const filteredData = getFilteredData();
  const totalSpent = spendingData.reduce((sum, entry, i) => selectedSpending[i] ? sum + entry.amount : sum, 0);

  const tabClasses = (tab) =>
    `px-3 py-1 rounded border ${
      timeframe === tab ? "bg-blue-600 text-white border-blue-600" : "bg-white text-black border-gray-300"
    }`;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">FinanceCoach</h1>
        <div className="space-x-4">
          <Dialog trigger={<Button className="bg-white text-black border">Add Today's Spending</Button>}>
            {({ close }) => (
              <>
                <h2 className="text-lg font-semibold mb-4">Enter Spending</h2>
                <Input
                  type="number"
                  placeholder="Amount"
                  onChange={(e) => setSpending(Number(e.target.value))}
                />
                <div className="mt-4 flex justify-end space-x-2">
                  <Button className="bg-gray-300 text-black" onClick={close}>Cancel</Button>
                  <Button
                    onClick={() => {
                      handleAddSpending();
                      close();
                    }}
                  >
                    Save
                  </Button>
                </div>
              </>
            )}
          </Dialog>
        </div>
      </nav>

      {/* Goal Progress Dashboard */}
      <main className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Your Progress</h2>
        <Card className="max-w-md mx-auto mb-6">
          <CardContent>
            <p className="text-lg">Goal: ${goal}</p>
            <p className="text-lg">Total Spent: ${totalSpent}</p>
            <div className="mt-2">
              <Button
                className="text-sm bg-gray-100 text-blue-700 hover:bg-gray-200"
                onClick={() => setShowDetails(!showDetails)}
              >
                {showDetails ? "Hide" : "Show"} Spending History
              </Button>
              {showDetails && (
                <>
                  <div className="flex justify-between items-center mt-2">
                    <Button className="text-xs" onClick={handleSelectAll}>Select All</Button>
                  </div>
                  <ul style={{listStyleType: 'none'}} className="mt-2 max-h-48 overflow-y-auto text-sm text-gray-700">
                    {spendingData.map((entry, idx) => (
                      <li key={idx} className="py-1 border-b flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={selectedSpending[idx]}
                            onChange={() => handleToggleSpending(idx)}
                          />
                          <span>{entry.time} — ${entry.amount}</span>
                          <button
                            className="text-red-500 hover:text-red-700 text-xs ml-2"
                            onClick={() => handleDeleteSpending(idx)}
                          >
                            🗑️
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>

                </>
              )}
            </div>
            <div className="mt-4">
              <Progress value={(totalSpent / goal) * 100} />
            </div>
          </CardContent>
        </Card>

        <div className="max-w-3xl mx-auto">
          <div className="flex space-x-2 mb-4 justify-end">
            <button onClick={() => setTimeframe("day")} className={tabClasses("day")}>1D</button>
            <button onClick={() => setTimeframe("week")} className={tabClasses("week")}>1W</button>
            <button onClick={() => setTimeframe("month")} className={tabClasses("month")}>1M</button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={filteredData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fontSize: 12 }} minTickGap={20} />
              <YAxis />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="cumulative"
                stroke="none"
                fill="#22c55e"
                fillOpacity={0.2}
              />
              <Line
                type="monotone"
                dataKey="amount"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </main>
    </div>
  );
}

