import BackgroundPattern from "@/components/background-pattern";
import AppHeader from "@/components/app-header";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <BackgroundPattern />
      <div className="flex flex-col gap-y-10 max-w-[1050px] mx-auto px-4 min-h-screen">
        <AppHeader />
        {children}
      </div>
    </>
  );
}
