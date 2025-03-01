"use client";
import DashboardSubButton from "./dashboard-sub-but";
type ExpensesListProps = {
  readonly expenses: {
    id: number;
    amount: number;
    description: string;
    date: Date;
  }[];
};

export default function ExpensesList({ expenses }: ExpensesListProps) {
  return (
    <ul className="h-[300px] bg-white rounded mt-4 shadow-md">
      {expenses.map((expense) => (
        <li key={expense.id} className="flex items-center px-4 py-2 border-b ">
          <p>{expense.description}</p>
          <p className="font-bold mr-[15px] ml-auto">{expense.amount}</p>
          <DashboardSubButton expense={expense.id} />
        </li>
      ))}
    </ul>
  );
}
