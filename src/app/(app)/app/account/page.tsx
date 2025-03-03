import { GetUserEmail } from "@/actions/client-side-actions";

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
    </div>
  );
}
