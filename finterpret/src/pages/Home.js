import { useState } from "react";
import { Button } from "../homepage-components/Button.js";
import { Card, CardContent } from "../homepage-components/Card.js";
import { Dialog } from "../homepage-components/Dialog.js";
import { Input } from "../homepage-components/Input.js";
import { Progress } from "../homepage-components/Progress.js";


import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Home() {
  const [spending, setSpending] = useState(0);
  const [goal, setGoal] = useState(1000);
  const [spendingData, setSpendingData] = useState([]);
  const [timeframe, setTimeframe] = useState("day");

  const handleAddSpending = () => {
    const now = new Date();
    const label = now.toLocaleString();
    setSpendingData([...spendingData, { time: label, amount: spending }]);
    alert("Spending saved!");
  };

  const getFilteredData = () => {
    if (spendingData.length <= 1) return spendingData.map((d, i) => ({ ...d, cumulative: d.amount }));

    const now = new Date();
    const dayMs = 24 * 60 * 60 * 1000;
    const weekMs = 7 * dayMs;
    const monthMs = 30 * dayMs;

    let cutoff;
    if (timeframe === "day") cutoff = now.getTime() - dayMs;
    else if (timeframe === "week") cutoff = now.getTime() - weekMs;
    else cutoff = now.getTime() - monthMs;

    const data = spendingData.filter(d => new Date(d.time).getTime() >= cutoff);
    let cumulative = 0;
    return data.map(d => {
      cumulative += d.amount;
      return { ...d, cumulative };
    });
  };

  const filteredData = getFilteredData();

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
          <Dialog
            trigger={<Button className="bg-white text-black border">Add Today's Spending</Button>}
          >
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
            <p className="text-lg">Spent: ${spending}</p>
            <div className="mt-4">
              <Progress value={(spending / goal) * 100} />
            </div>
          </CardContent>
        </Card>

{/* TODO: Make spending progress chart into component */}
        <div className="max-w-3xl mx-auto">
          <div className="flex space-x-2 mb-4 justify-end">
            <button onClick={() => setTimeframe("day")} className={tabClasses("day")}>1D</button>
            <button onClick={() => setTimeframe("week")} className={tabClasses("week")}>1W</button>
            <button onClick={() => setTimeframe("month")} className={tabClasses("month")}>1M</button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={filteredData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fontSize: 12 }} minTickGap={20} />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="cumulative"
                stroke="#93c5fd"
                strokeWidth={2}
                dot={false}
                opacity={0.3}
              />
              <Line
                type="monotone"
                dataKey="amount"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </main>
    </div>
  );
}