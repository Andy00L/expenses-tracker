"use client";
import { createCheckoutSession } from "@/actions/server-side-actions";
import { useRouter } from "next/navigation";
export default function SubscriptionBtn() {
  const router = useRouter();
  return (
    <button
      onClick={async () => {
        await createCheckoutSession();
        router.refresh();
      }}
      className="bg-blue-500 text-white px-4 py-2 rounded-md m-4"
    >
      Pay To Upgrade
    </button>
  );
}
