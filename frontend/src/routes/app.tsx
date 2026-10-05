import { createFileRoute, Outlet, useLocation } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AppSidebar, MobileNav } from "@/components/app/AppSidebar";
import { Toaster } from "@/components/ui/sonner";

export const Route = createFileRoute("/app")({
  component: AppLayout,
});

function AppLayout() {
  const { pathname } = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  useEffect(() => { setCollapsed(localStorage.getItem("mc-sidebar") === "1"); }, []);
  const toggle = () => setCollapsed((c) => { localStorage.setItem("mc-sidebar", c ? "0" : "1"); return !c; });
  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar collapsed={collapsed} onToggle={toggle} />
      <div className="min-w-0 flex-1 pb-28 md:pb-16">
        <MobileNav />
        <main className="relative mx-auto max-w-6xl px-4 pt-6 md:px-10 md:pt-12">
          <div key={pathname} className="animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
      <Toaster />
    </div>
  );
}
