import Link from "next/link";

export default function Home() {
  return (
    <div>
      <h1 className="text-4xl font-bold">Expense Tracker</h1>
      <Link href="app/dashboard">dashboard</Link>
    </div>
  );
}
