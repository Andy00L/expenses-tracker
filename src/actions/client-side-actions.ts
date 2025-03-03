"use client";

import { useUser } from "@clerk/nextjs";

export function GetUserEmail() {
  const { user } = useUser();
  const email = user?.emailAddresses[0].emailAddress;
  return email;
}
