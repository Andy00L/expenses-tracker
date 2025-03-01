import { addExpense } from "@/actions/actions";

export default function ExpensesForm() {
  return (
    <form
      action={addExpense}
      className="w-full mt-8 rounded overflow-hidden bg-white"
    >
      <input
        type="text"
        name="description"
        placeholder="description"
        className="w-full px-3 py-2 outline-none"
      />
      <input
        type="number"
        name="amount"
        placeholder="amount"
        className="w-full px-3 py-2 outline-none"
      />
      <button
        type="submit"
        className="w-full bg-blue-500 text-white px-2 py-2 font-bold"
      >
        Add Expense
      </button>
    </form>
  );
}
