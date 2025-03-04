import { getUserId } from "@/actions/server-side-actions";
import ExpensesForm from "@/components/expenses-form";
import ExpensesList from "@/components/expenses-list";
import { prisma } from "@/lib/db";
import { redirect } from "next/navigation";
export default async function Page() {
  const userId = await getUserId();
  //authorize user
  const subscription = await prisma.subscription.findFirst({
    where: {
      userId: userId as string,
    },
  });

  if (!subscription || subscription.status !== "active") {
    return redirect("/app/account");
  }

  const expenses = await prisma.expense.findMany({
    where: {
      creatorId: userId as string,
    },
  });

  return (
    <div>
      <div className="flex justify-center items-center ">
        <h1 className="text-3xl font-bold text-white ">Dashboard</h1>
      </div>

      <div className=" w-full max-w-[600px] mx-auto ">
        <ExpensesList expenses={expenses} />

        <ExpensesForm />
      </div>
    </div>
  );
}
