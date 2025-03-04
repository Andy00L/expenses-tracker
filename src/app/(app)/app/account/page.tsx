import { GetUserEmail } from "@/actions/client-side-actions";
import SubscriptionBtn from "@/components/subscription-btn";
export default function Page() {
  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold text-white text-center">Account</h1>

      <p className="text-white mt-2">
        Logged in with email:{" "}
        <span className="font-bold">
          <GetUserEmail />
        </span>
      </p>
      <div className="mt-30 border bg-black/50 border-white/10 p-4 rounded-md max-w-[400px] mx-auto h-[300px]">
        <h1 className="text-white text-2xl font-bold">Subscription</h1>
        <p className="text-white text-sm p-4">
          You are currently on the free plan. Upgrade to the pro plan to unlock
          all features.
        </p>
        <ol className=" bg-black/50 border border-white/10 p-4 rounded-md font-bold text-left">
          <li className="text-white text-sm">Ai recommendation</li>
          <li className="text-white text-sm">Expense blocker</li>
          <li className="text-white text-sm">Investment auto-tracker</li>
          <li className="text-white text-sm">Cash Back Finder</li>
        </ol>
        <SubscriptionBtn />
      </div>
    </div>
  );
}
