import { ClerkProvider } from "@clerk/nextjs";
import Image from "next/image";
import Link from "next/link";
import HeaderButtons from "./header-buttons";

export default function AppHeader() {
  return (
    <ClerkProvider>
      <header className="flex items-center border-b border-white/10 py-2">
        <Link href="/app/dashboard">
          <Image
            src="https://bytegrad.com/course-assets/youtube/expensestracker/logo.png"
            alt="logo"
            width={25}
            height={25}
          />
        </Link>
        <HeaderButtons />
      </header>
    </ClerkProvider>
  );
}
