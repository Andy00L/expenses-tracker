"use server";
import { prisma } from "@/lib/db";
import { auth, currentUser } from "@clerk/nextjs/server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import Stripe from "stripe";

async function serverSideEmail() {
  const user = await currentUser();
  return user?.emailAddresses[0].emailAddress;
}

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

export async function createCheckoutSession() {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
    apiVersion: "2025-02-24.acacia",
  });

  const userEmail = await serverSideEmail();
  const userId = await getUserId();
  const session = await stripe.checkout.sessions.create({
    customer_email: userEmail as string,
    client_reference_id: userId as string,
    line_items: [
      {
        price: "price_1Qyr0HCEq45hckvnjIY773BA",
        quantity: 1,
      },
    ],
    mode: "payment",
    success_url: `http://localhost:3000/app/dashboard`,
    cancel_url: `http://localhost:3000/app/account`,
  });
  redirect(session.url as string);
}
