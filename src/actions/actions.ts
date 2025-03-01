"use server";

import { prisma } from "@/lib/db";
import { revalidatePath } from "next/cache";

export async function addExpense(formData: FormData) {
  await prisma.expense.create({
    data: {
      amount: Number(formData.get("amount")),
      description: formData.get("description") as string,
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
