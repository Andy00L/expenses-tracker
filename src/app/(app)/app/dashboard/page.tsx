import Link from "next/link";
import ExpensesList from "@/components/expenses-list";
import ExpensesForm from "@/components/expenses-form";
export default function Page() {
  return (
    <div>
      <div>
        <h1 className="text-3xl font-bold text-white text-center">Dashboard</h1>
        <div className=" w-full max-w-[600px] mx-auto">
          <ExpensesList />
          <ExpensesForm />
        </div>
      </div>

      <h1>Dashboard</h1>
      <Link href="/app/account">Account</Link>
      <br />
      <Link href="/">main</Link>
    </div>
  );
}
