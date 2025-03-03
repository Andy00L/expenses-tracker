"use client";
import { deleteExpense } from "@/actions/server-side-actions";

export default function dashboardSubButton({ expense }: { expense: number }) {
  return (
    <button
      onClick={async () => {
        await deleteExpense(expense);
      }}
      className="bg-red-500 text-[10px] h-[20px] w-[20px] text-white rounded-full hover:bg-red-600 transition"
    >
      X
    </button>
  );
}
