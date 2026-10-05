import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowRight, CheckCircle2, Clock, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { mcButton, Reveal } from "@/components/mathcook/primitives";
import { TOPICS } from "@/components/mathcook/topics";
import type { Cook } from "@/lib/mathcook/data";
import { MathView } from "@/components/ui/MathView";
import { cn } from "@/lib/utils";

export const topicMeta = (name: string) => TOPICS.find((t) => t.name === name) ?? TOPICS[0]!;

export function PageHeader({ eyebrow, title, sub, children }: { eyebrow?: ReactNode; title: ReactNode; sub?: string; children?: ReactNode }) {
  return (
    <Reveal className="mb-10">
      {eyebrow}
      <h1 className="mt-4 text-4xl font-black leading-[1.05] md:text-6xl">{title}</h1>
      {sub && <p className="mt-4 max-w-2xl text-lg text-muted-foreground">{sub}</p>}
      {children}
    </Reveal>
  );
}

export function FloatingGlyphs() {
  const g = [
    ["π", "left-[6%] top-24 animate-floaty"], ["∑", "right-[8%] top-40 animate-drift"],
    ["√", "left-[12%] bottom-24 animate-drift"], ["x²", "right-[14%] bottom-10 animate-floaty"],
  ];
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
      {g.map(([s, c]) => (
        <span key={s} className={cn("absolute font-display text-5xl font-black text-primary/15 md:text-7xl", c)}>{s}</span>
      ))}
    </div>
  );
}

export function ProgressBar({ value, tone = "bg-primary" }: { value: number; tone?: string }) {
  return (
    <div className="h-3 w-full overflow-hidden rounded-full bg-muted">
      <div className={cn("h-full rounded-full transition-[width] duration-1000 ease-out", tone)} style={{ width: `${value}%` }} />
    </div>
  );
}

export function CookCard({ cook }: { cook: Cook }) {
  const t = topicMeta(cook.topic);
  return (
    <Link to="/app/solve/$id" params={{ id: cook.id }} className="group card-lift flex flex-col rounded-3xl border border-border bg-card p-6 shadow-soft">
      <div className="flex items-center justify-between">
        <span className={cn("grid h-11 w-11 place-items-center rounded-2xl font-display font-black", t.tone)}>{t.glyph}</span>
        <span className="text-sm text-muted-foreground">{cook.date}</span>
      </div>
      <div className="mt-5 font-display text-2xl font-black">
        <MathView math={cook.problem} />
      </div>
      <p className="mt-1 text-sm font-semibold text-muted-foreground">{cook.topic} · {cook.skill}</p>
      <div className="mt-6 flex items-center justify-between">
        {cook.status === "solved" ? (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-success/15 px-3 py-1 text-sm font-bold text-success"><CheckCircle2 className="h-4 w-4" />Solved</span>
        ) : (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-t-sun/20 px-3 py-1 text-sm font-bold text-foreground"><Clock className="h-4 w-4" />In progress</span>
        )}
        <span className="inline-flex items-center gap-1 font-display text-sm font-extrabold text-primary">
          View Solution <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </span>
      </div>
    </Link>
  );
}

export function EmptyState({ icon: Icon, title, sub, cta, to }: { icon: LucideIcon; title: string; sub?: string; cta: string; to: "/app" | "/app/learn" | "/app/solve" }) {
  return (
    <div className="relative overflow-hidden rounded-[2rem] bg-primary-soft px-6 py-16 text-center">
      <span className="mx-auto grid h-20 w-20 animate-floaty place-items-center rounded-3xl bg-card text-primary shadow-soft"><Icon className="h-9 w-9" /></span>
      <h3 className="mt-6 text-3xl font-black">{title}</h3>
      {sub && <p className="mx-auto mt-3 max-w-md text-muted-foreground">{sub}</p>}
      <Link to={to} className={cn(mcButton(), "mt-8")}>{cta} <ArrowRight className="h-4 w-4" /></Link>
    </div>
  );
}

export function useAnimated(v: number) {
  const [x, setX] = useState(0);
  useEffect(() => { const t = setTimeout(() => setX(v), 200); return () => clearTimeout(t); }, [v]);
  return x;
}
