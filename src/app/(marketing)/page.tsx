import Link from "next/link";
import Image from "next/image";

export default function Home() {
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
        <h1 className="text-5xl font-semibold my-6 max-w-[500px]">
          Track your expenses with ease
        </h1>
        <p className="text-2xl font-medium max-w-[600px]">
          Use <span className="font-extrabold">Expense</span> Tracker to easily
          keep track of your expenses. Get lifetime access for 99$.
        </p>
      </div>
      <Link href="/app/dashboard" className="bg-white px-6 py-3 rounded-lg">
        Dashboard
      </Link>
    </div>
  );
}
