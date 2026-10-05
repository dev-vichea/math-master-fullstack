import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Camera, Check, Circle, Keyboard, Flame } from "lucide-react";
import { useEffect, useState } from "react";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { FloatingGlyphs, ProgressBar, useAnimated } from "@/components/app/shared";
import { SKILL_MASTERY, STUDENT, TODAY_TASKS } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/")({
  head: () => pageMeta("Home — MathCook", "Your personal MathCook dashboard: continue learning, today's goal and quick cooks."),
  component: HomeDashboard,
});

function useGreeting() {
  const [g, setG] = useState("Hello");
  useEffect(() => { const h = new Date().getHours(); setG(h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening"); }, []);
  return g;
}

function HomeDashboard() {
  const g = useGreeting();
  const cont = useAnimated(78);
  const goal = useAnimated((STUDENT.todayMin / STUDENT.goalMin) * 100);
  return (
    <div className="relative">
      <FloatingGlyphs />
      <Reveal>
        <p className="font-display font-bold text-muted-foreground">{g}, {STUDENT.name} 👋</p>
        <h1 className="mt-2 text-4xl font-black md:text-6xl">Ready to <span className="text-primary">cook</span> some math?</h1>
      </Reveal>

      <div className="mt-10 grid gap-5 lg:grid-cols-[1.5fr_1fr]">
        <Reveal className="relative overflow-hidden rounded-[2rem] bg-primary p-8 text-primary-foreground shadow-float md:p-10">
          <span aria-hidden className="absolute -right-6 -top-10 animate-drift font-display text-[10rem] font-black opacity-10">∫</span>
          <span className="font-display text-xs font-black uppercase tracking-[0.18em] opacity-80">Continue learning · Grade 12</span>
          <h2 className="mt-3 text-3xl font-black md:text-4xl">Calculus → Derivatives</h2>
          <div className="mt-6 flex items-center gap-4">
            <div className="h-3 flex-1 overflow-hidden rounded-full bg-primary-foreground/20"><div className="h-full rounded-full bg-primary-foreground transition-[width] duration-1000" style={{ width: `${cont}%` }} /></div>
            <span className="font-display font-black">78%</span>
          </div>
          <Link to="/app/learn" className={cn(mcButton({ variant: "inverse" }), "mt-8")}>Continue Learning <ArrowRight className="h-4 w-4" /></Link>
        </Reveal>

        <Reveal delay={100} className="rounded-[2rem] border border-border bg-card p-7 shadow-soft">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-black">Today's Math Goal</h2>
            <span className="inline-flex items-center gap-1 rounded-full bg-t-coral/15 px-3 py-1 text-sm font-bold text-t-coral"><Flame className="h-4 w-4" />{STUDENT.streak}</span>
          </div>
          <p className="mt-4 font-display text-3xl font-black">{STUDENT.todayMin} <span className="text-lg text-muted-foreground">/ {STUDENT.goalMin} min</span></p>
          <div className="mt-3"><ProgressBar value={goal} /></div>
          <ul className="mt-5 space-y-2.5">
            {TODAY_TASKS.map((t) => (
              <li key={t.label} className="flex items-center gap-3 font-semibold">
                {t.done ? <span className="grid h-6 w-6 place-items-center rounded-full bg-success text-primary-foreground"><Check className="h-3.5 w-3.5" /></span> : <Circle className="h-6 w-6 text-border" />}
                <span className={cn(t.done && "text-muted-foreground line-through")}>{t.label}</span>
              </li>
            ))}
          </ul>
        </Reveal>
      </div>

      <Reveal delay={150} className="mt-12">
        <Eyebrow>Quick cook</Eyebrow>
        <div className="mt-5 grid gap-5 sm:grid-cols-2">
          {[
            { icon: Camera, t: "Upload Problem", s: "Upload a worksheet or math problem.", tone: "bg-primary text-primary-foreground" },
            { icon: Keyboard, t: "Type Problem", s: "Enter an equation or math question.", tone: "bg-card text-primary" },
          ].map(({ icon: Icon, t, s, tone }) => (
            <Link key={t} to="/app/solve" className="group card-lift flex items-center gap-5 rounded-[2rem] bg-primary-soft p-6">
              <span className={cn("grid h-14 w-14 shrink-0 place-items-center rounded-2xl shadow-soft", tone)}><Icon className="h-6 w-6" /></span>
              <div className="flex-1"><h3 className="text-xl font-black">{t}</h3><p className="text-muted-foreground">{s}</p></div>
              <ArrowRight className="h-5 w-5 text-primary transition-transform group-hover:translate-x-1" />
            </Link>
          ))}
        </div>
      </Reveal>

      <Reveal delay={200} className="mt-12">
        <div className="flex items-end justify-between"><h2 className="text-3xl font-black">Your Skills</h2>
          <Link to="/app/progress" className="font-display font-extrabold text-primary hover:underline">All progress →</Link></div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {SKILL_MASTERY.map((s) => <SkillTile key={s.name} {...s} />)}
        </div>
      </Reveal>
    </div>
  );
}

function SkillTile({ name, value, glyph, tone }: { name: string; value: number; glyph: string; tone: string }) {
  const v = useAnimated(value);
  const r = 34, c = 2 * Math.PI * r;
  return (
    <div className="card-lift flex flex-col items-center rounded-3xl border border-border bg-card p-5 text-center shadow-soft">
      <div className="relative h-24 w-24">
        <svg viewBox="0 0 80 80" className="h-full w-full -rotate-90">
          <circle cx="40" cy="40" r={r} strokeWidth="7" className="fill-none stroke-muted" />
          <circle cx="40" cy="40" r={r} strokeWidth="7" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c - (v / 100) * c}
            className={cn("fill-none stroke-current transition-[stroke-dashoffset] duration-1000", tone.replace("bg-", "text-"))} />
        </svg>
        <span className="absolute inset-0 grid place-items-center font-display text-lg font-black">{glyph}</span>
      </div>
      <p className="mt-3 font-display font-black">{name}</p>
      <p className="text-sm font-bold text-muted-foreground">{value}%</p>
    </div>
  );
}
