"use server";
import { prisma } from "@/lib/db";
import { revalidatePath } from "next/cache";
import { auth } from "@clerk/nextjs/server";
export async function addExpense(formData: FormData) {
  const authData = await auth();
  const userId = authData.userId;

  await prisma.expense.create({
    data: {
      amount: Number(formData.get("amount")),
      description: formData.get("description") as string,
      creatorId: userId as string,
    },
  });
  revalidatePath("/app/dashboard");
}

export async function deleteExpense(id: number) {
  await prisma.expense.delete({
    where: { id },
  });
  revalidatePath("/app/dashboard");
}

export async function editExpense(formData: FormData) {
  await prisma.expense.update({
    where: { id: Number(formData.get("id")) },
    data: {
      amount: Number(formData.get("amount")),
      description: formData.get("description") as string,
    },
  });
  revalidatePath("/app/dashboard");
}

export async function getUserId() {
  const authData = await auth();
  const userId = authData.userId;
  return userId;
}
