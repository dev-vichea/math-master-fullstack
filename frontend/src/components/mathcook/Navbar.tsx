import { useEffect, useState } from "react";
import { ArrowRight, Menu, X } from "lucide-react";
import { Logo, mcButton } from "./primitives";
import { cn } from "@/lib/utils";

const LINKS = [
  { label: "Solve", href: "#solve" },
  { label: "Learn", href: "#learn" },
  { label: "Topics", href: "#topics" },
  { label: "How It Works", href: "#how" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const on = () => setScrolled(window.scrollY > 12);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);

  return (
    <header className="sticky top-0 z-50 px-3 pt-3 md:px-6">
      <nav
        className={cn(
          "mx-auto flex max-w-7xl items-center justify-between rounded-full px-4 py-2.5 transition-all duration-300 md:px-6",
          scrolled ? "bg-card/85 shadow-soft backdrop-blur-xl" : "bg-transparent",
        )}
      >
        <a href="#top" aria-label="MathCook home">
          <Logo />
        </a>
        <ul className="hidden items-center gap-1 lg:flex">
          {LINKS.map((l) => (
            <li key={l.href}>
              <a href={l.href} className="rounded-full px-4 py-2 font-display font-bold text-muted-foreground transition-colors hover:bg-primary-soft hover:text-primary">
                {l.label}
              </a>
            </li>
          ))}
        </ul>
        <div className="hidden items-center gap-2 lg:flex">
          <a href="/app" className={mcButton({ variant: "ghost", size: "sm" })}>Log In</a>
          <a href="#solve" className={mcButton({ size: "sm" })}>
            Start Cooking <ArrowRight className="h-4 w-4" />
          </a>
        </div>
        <button className="rounded-full p-2 lg:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu">
          {open ? <X /> : <Menu />}
        </button>
      </nav>
      {open && (
        <div className="mx-auto mt-2 max-w-7xl rounded-3xl bg-card p-4 shadow-float lg:hidden">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="block rounded-2xl px-4 py-3 font-display text-lg font-bold hover:bg-primary-soft">
              {l.label}
            </a>
          ))}
          <div className="mt-3 grid gap-2">
            <a href="/app" className={mcButton({ variant: "outline" })}>Log In</a>
            <a href="#solve" onClick={() => setOpen(false)} className={mcButton()}>Start Cooking <ArrowRight className="h-4 w-4" /></a>
          </div>
        </div>
      )}
    </header>
  );
}
