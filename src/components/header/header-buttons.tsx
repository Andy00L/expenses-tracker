"use client";

import { UserButton } from "@clerk/nextjs";
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
export default function HeaderButtons() {
  const pathname = usePathname();

  return (
    <nav className="ml-auto">
      <ul className="flex text-xs gap-2 mt-4">
        {routes.map((route) => (
          <li key={route.href} className="mt-1">
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
        <li>{pathname !== "/app/account" && <UserButton />}</li>
      </ul>
    </nav>
  );
}
