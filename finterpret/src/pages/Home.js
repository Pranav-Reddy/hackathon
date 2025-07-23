import { useState } from "react";
import { Button } from "../homepage-components/Button.js";
import { Card, CardContent } from "../homepage-components/Card.js";
import { Dialog } from "../homepage-components/Dialog.js";
import { Input } from "../homepage-components/Input.js";
import { Progress } from "../homepage-components/Progress.js";

export default function Home() {
  const [spending, setSpending] = useState(0);
  const [goal, setGoal] = useState(1000);

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
                  <Button onClick={() => { alert("Spending saved!"); close(); }}>Save</Button>
                </div>
              </>
            )}
          </Dialog>
          <Button className="bg-white text-black">Goals</Button>
          <Button className="bg-white text-black">Advisor</Button>
          <Button className="bg-white text-black">Settings</Button>
        </div>
      </nav>

      {/* Goal Progress Dashboard */}
      <main className="p-6">
        <h2 className="text-2xl font-semibold mb-4">Your Progress</h2>
        <Card className="max-w-md mx-auto">
          <CardContent>
            <p className="text-lg">Goal: ${goal}</p>
            <p className="text-lg">Spent: ${spending}</p>
            <div className="mt-4">
              <Progress value={(spending / goal) * 100} />
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
