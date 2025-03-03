import { SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";
import { auth } from "@clerk/nextjs/server";
import Image from "next/image";

export default async function Home() {
  const { userId, redirectToSignIn } = await auth();

  if (userId) return redirectToSignIn();
  return (
    <div className="bg-[#5DC9A8] min-h-screen flex flex-col xl:flex-row items-center justify-center gap-10">
      <Image
        src="https://bytegrad.com/course-assets/youtube/expensestracker/preview.png"
        alt="Expense Tracker app preview"
        width={700}
        height={472}
        className="rounded-mg"
      />
      <div>
        <div>
          <h1 className="text-5xl font-semibold my-6 max-w-[500px]">
            Track your expenses with ease
          </h1>
          <p className="text-2xl font-medium max-w-[600px]">
            Use <span className="font-extrabold">Expense</span> Tracker to
            easily keep track of your expenses. Get lifetime access for 99$.
          </p>
        </div>

        <div className="mx-auto mt-7  justify-center space-x-3 items-center flex flex-row gap-y-10">
          <SignedOut>
            <div className="group cursor-pointer">
              <div className="bg-black text-white px-4 py-2 rounded-lg font-medium transition-all duration-300 transform group-hover:scale-105 group-hover:shadow-lg">
                <SignInButton mode="modal" />
              </div>
            </div>

            <div className="group cursor-pointer">
              <div className="bg-black/50 text-white px-4 py-2 rounded-lg font-medium  transition-all duration-300 transform group-hover:scale-105 group-hover:shadow-lg">
                <SignUpButton mode="modal" />
              </div>
            </div>
          </SignedOut>
        </div>
      </div>
    </div>
  );
}
