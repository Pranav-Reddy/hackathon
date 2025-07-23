import { useState } from "react";

export function Dialog({ trigger, children }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <div onClick={() => setOpen(true)}>{trigger}</div>
      {open && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-96">
            {children({ close: () => setOpen(false) })}
          </div>
        </div>
      )}
    </>
  );
}
