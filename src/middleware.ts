import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isProtectedRoute = createRouteMatcher(["/app/dashboard", "/app/account"]);
const isMarketingRoute = createRouteMatcher(["/"]);

export default clerkMiddleware(async (auth, req) => {
  const session = await auth();

  // If user is authenticated and tries to access marketing page, redirect to dashboard
  if (session.userId && isMarketingRoute(req)) {
    return NextResponse.redirect(new URL("/app/dashboard", req.url));
  }

  // Protect app routes for unauthenticated users
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
  ],
};
