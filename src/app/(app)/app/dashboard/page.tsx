import Link from "next/link";

export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Link href="/app/account">Account</Link>
      <br />
      <Link href="/">main</Link>
    </div>
  );
}
