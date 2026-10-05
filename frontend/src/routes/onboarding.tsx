import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { ArrowLeft, ArrowRight, Check } from "lucide-react";
import { useState } from "react";
import { Logo, mcButton } from "@/components/mathcook/primitives";
import { FloatingGlyphs } from "@/components/app/shared";
import { GRADES } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/onboarding")({
  head: () => pageMeta("Get started — MathCook", "Tell MathCook your grade, goals and study time to build your personal plan."),
  component: Onboarding,
});

const GOALS = ["Algebra", "Geometry", "Calculus", "Trigonometry", "Problem Solving", "Exam Preparation"];
const TIMES = ["15 min", "30 min", "45 min", "1 hour+"];

function Onboarding() {
  const nav = useNavigate();
  const [step, setStep] = useState(0);
  const [grade, setGrade] = useState<number | null>(null);
  const [goals, setGoals] = useState<string[]>([]);
  const [time, setTime] = useState<string | null>(null);
  const can = [grade !== null, goals.length > 0, time !== null][step];
  const opt = (on: boolean) => cn("rounded-3xl p-5 font-display text-lg font-black ring-2 transition-all", on ? "bg-primary text-primary-foreground ring-primary shadow-float" : "bg-card ring-border hover:ring-primary");
  // Future: persist { grade, goals, time } to the backend to personalise the dashboard & study plan.
  return (
    <div className="relative min-h-screen px-4 py-8">
      <FloatingGlyphs />
      <div className="mx-auto max-w-3xl">
        <div className="flex items-center justify-between"><Link to="/"><Logo /></Link><Link to="/app" className="font-display font-bold text-muted-foreground">Skip</Link></div>
        <div className="mt-10 flex gap-2">{[0, 1, 2].map((n) => <span key={n} className={cn("h-2 flex-1 rounded-full transition-colors", n <= step ? "bg-primary" : "bg-muted")} />)}</div>
        <div key={step} className="mt-12 animate-fade-in">
          {step === 0 && (<>
            <h1 className="text-4xl font-black md:text-5xl">What grade are you studying?</h1>
            <div className="mt-8 grid grid-cols-3 gap-3 sm:grid-cols-4">{GRADES.map((g) => <button key={g} onClick={() => setGrade(g)} className={opt(grade === g)}>Grade {g}</button>)}</div>
          </>)}
          {step === 1 && (<>
            <h1 className="text-4xl font-black md:text-5xl">What do you want to improve?</h1>
            <p className="mt-3 text-muted-foreground">Pick as many as you like.</p>
            <div className="mt-8 grid gap-3 sm:grid-cols-2">{GOALS.map((g) => { const on = goals.includes(g); return (
              <button key={g} onClick={() => setGoals((x) => on ? x.filter((y) => y !== g) : [...x, g])} className={cn(opt(on), "flex items-center justify-between text-left")}>{g}{on && <Check className="h-5 w-5" />}</button>); })}</div>
          </>)}
          {step === 2 && (<>
            <h1 className="text-4xl font-black md:text-5xl">How much time can you study each day?</h1>
            <div className="mt-8 grid grid-cols-2 gap-3 md:grid-cols-4">{TIMES.map((t) => <button key={t} onClick={() => setTime(t)} className={cn(opt(time === t), "py-8")}>{t}</button>)}</div>
          </>)}
        </div>
        <div className="mt-12 flex justify-between">
          <button onClick={() => setStep(step - 1)} className={cn(mcButton({ variant: "ghost" }), step === 0 && "invisible")}><ArrowLeft className="h-4 w-4" />Back</button>
          <button disabled={!can} onClick={() => step < 2 ? setStep(step + 1) : nav({ to: "/app" })} className={cn(mcButton({ size: "lg" }), !can && "pointer-events-none opacity-40")}>
            {step < 2 ? "Continue" : "Start cooking"} <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
