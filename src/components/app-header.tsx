"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
const routes = [
  {
    label: "Dashboard",
    href: "/app/dashboard",
  },
  {
    label: "Account",
    href: "/app/account",
  },
];

export default function AppHeader() {
  const pathname = usePathname();

  return (
    <header className="flex justify-between items-center border-b border-white/10 py-2">
      <Link href="/app/dashboard">
        <Image
          src="https://bytegrad.com/course-assets/youtube/expensestracker/logo.png"
          alt="logo"
          width={25}
          height={25}
        />
      </Link>
      <nav>
        <ul className="flex text-xs gap-2">
          {routes.map((route) => (
            <li key={route.href}>
              <Link
                href={route.href}
                className={`px-2 py-1 hover:text-white transition text-white/100  rounded-sm ${
                  route.href === pathname ? " bg-white/10" : ""
                }`}
              >
                {route.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
