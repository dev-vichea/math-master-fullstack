import { Link, useRouterState } from "@tanstack/react-router";
import {
  Home, BookOpen, ChefHat, FlaskConical, ClipboardCheck, FileText, Library, CalendarDays, BarChart3,
  Settings, PanelLeftClose, PanelLeftOpen, MoreHorizontal, X, Bell,
} from "lucide-react";
import { useState } from "react";
import { Logo } from "@/components/mathcook/primitives";
import { USER } from "@/lib/mathcook/data";
import { cn } from "@/lib/utils";

export const NAV = [
  { label: "Home", to: "/app", icon: Home },
  { label: "Learn", to: "/app/learn", icon: BookOpen },
  { label: "Solve", to: "/app/solve", icon: ChefHat },
  { label: "Practice", to: "/app/practice", icon: FlaskConical },
  { label: "Quiz", to: "/app/quiz", icon: ClipboardCheck },
  { label: "Exams", to: "/app/exams", icon: FileText },
  { label: "Library", to: "/app/library", icon: Library },
  { label: "Study Plan", to: "/app/plan", icon: CalendarDays },
  { label: "Progress", to: "/app/progress", icon: BarChart3 },
] as const;

function useIsActive() {
  const path = useRouterState({ select: (s) => s.location.pathname });
  return (to: string) => (to === "/app" ? path === "/app" || path === "/app/" : path.startsWith(to));
}

export function AppSidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const isActive = useIsActive();
  const item = (active: boolean) =>
    cn(
      "group relative flex items-center gap-3 rounded-full px-4 py-2.5 font-display text-sm font-bold transition-all duration-150",
      active
        ? "-translate-y-0.5 bg-primary text-primary-foreground shadow-[0_5px_0_0_var(--primary-deep)] active:translate-y-0 active:shadow-[0_1px_0_0_var(--primary-deep)]"
        : "text-muted-foreground hover:bg-muted/60 hover:text-foreground active:translate-y-0.5",
      collapsed && "justify-center px-0 h-11 w-11 mx-auto"
    );
  return (
    <aside className={cn("sticky top-0 hidden h-screen shrink-0 flex-col border-r border-border bg-card/60 p-4 backdrop-blur-xl transition-[width] duration-300 md:flex", collapsed ? "w-20" : "w-64")}>
      <div className={cn("flex items-center justify-between", collapsed && "flex-col gap-3")}>
        <Link to="/app" aria-label="MathCook home">{collapsed ? <Logo className="[&>span:last-child]:hidden" /> : <Logo />}</Link>
        <button onClick={onToggle} aria-label="Toggle sidebar" className="rounded-xl p-2 text-muted-foreground hover:bg-muted">
          {collapsed ? <PanelLeftOpen className="h-5 w-5" /> : <PanelLeftClose className="h-5 w-5" />}
        </button>
      </div>
      <nav className="mt-6 flex-1 space-y-2.5 overflow-y-auto px-1 py-1">
        {NAV.map(({ label, to, icon: Icon }) => (
          <Link key={to} to={to} title={collapsed ? label : undefined} className={item(isActive(to))}>
            <Icon className="h-5 w-5 shrink-0" />{!collapsed && label}
          </Link>
        ))}
      </nav>
      <div className="space-y-2.5 border-t border-border/80 pt-3">
        <Link to="/app/settings" title={collapsed ? "Settings" : undefined} className={item(isActive("/app/settings"))}>
          <Settings className="h-5 w-5 shrink-0" />{!collapsed && "Settings"}
        </Link>
        <div className={cn("mt-2 flex items-center gap-3 rounded-full border border-border/70 bg-card/50 p-1.5 transition-colors hover:bg-muted/40", collapsed ? "justify-center p-1.5" : "pl-2 pr-4")}>
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary font-display text-xs font-black text-primary-foreground">{USER.initials}</span>
          {!collapsed && <div className="min-w-0"><p className="truncate font-display text-sm font-bold text-foreground">{USER.name}</p><p className="text-[11px] text-muted-foreground">Grade 12 · 🔥 7 days</p></div>}
        </div>
      </div>
    </aside>
  );
}

export function MobileNav() {
  const isActive = useIsActive();
  const [more, setMore] = useState(false);
  const primary = NAV.slice(0, 4);
  const rest = [...NAV.slice(4), { label: "Settings", to: "/app/settings", icon: Settings } as const];
  return (
    <>
      <header className="sticky top-0 z-40 flex items-center justify-between bg-background/85 px-4 py-3 backdrop-blur-xl md:hidden">
        <Link to="/app"><Logo /></Link>
        <div className="flex items-center gap-2">
          <button aria-label="Notifications" className="rounded-full p-2 text-muted-foreground"><Bell className="h-5 w-5" /></button>
          <span className="grid h-9 w-9 place-items-center rounded-full bg-primary font-display text-sm font-black text-primary-foreground">{USER.initials}</span>
        </div>
      </header>
      <nav className="fixed inset-x-3 bottom-3 z-50 flex rounded-full border border-border/70 bg-card/95 p-1.5 shadow-float backdrop-blur-xl md:hidden">
        {primary.map(({ label, to, icon: Icon }) => (
          <Link key={to} to={to} className={cn("flex flex-1 flex-col items-center gap-0.5 rounded-full py-1.5 font-display text-[11px] font-bold transition-all duration-150",
            isActive(to)
              ? "-translate-y-0.5 bg-primary text-primary-foreground shadow-[0_3px_0_0_var(--primary-deep)]"
              : "text-muted-foreground hover:bg-muted/70 hover:text-foreground active:translate-y-0.5")}>
            <Icon className="h-5 w-5" />{label}
          </Link>
        ))}
        <button onClick={() => setMore(true)} className="flex flex-1 flex-col items-center gap-0.5 rounded-full py-1.5 font-display text-[11px] font-semibold text-muted-foreground transition-all duration-150 hover:bg-muted/70 hover:text-foreground">
          <MoreHorizontal className="h-5 w-5" />More
        </button>
      </nav>
      {more && (
        <div className="fixed inset-0 z-50 bg-foreground/20 md:hidden" onClick={() => setMore(false)}>
          <div className="absolute inset-x-3 bottom-3 animate-fade-in rounded-[2rem] bg-card p-4 shadow-float" onClick={(e) => e.stopPropagation()}>
            <div className="mb-2 flex items-center justify-between px-2"><span className="font-display font-black">More</span>
              <button onClick={() => setMore(false)} aria-label="Close" className="rounded-full p-2"><X className="h-5 w-5" /></button></div>
            <div className="grid grid-cols-3 gap-2">
              {rest.map(({ label, to, icon: Icon }) => (
                <Link key={to} to={to} onClick={() => setMore(false)} className={cn("flex flex-col items-center gap-2 rounded-xl p-3 font-display text-sm font-semibold transition-all duration-150",
                  isActive(to)
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-muted/70 hover:text-foreground")}>
                  <Icon className="h-6 w-6" />{label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
