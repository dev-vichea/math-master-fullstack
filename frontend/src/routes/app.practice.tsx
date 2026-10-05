import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Sparkles, BookOpen, RotateCcw, Zap, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { mcButton, Reveal } from "@/components/mathcook/primitives";
import { PageHeader } from "@/components/app/shared";
import { GRADES } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/practice")({
  head: () => pageMeta("Practice — MathCook", "Adaptive practice for your weak topics, current lesson, past mistakes and quick sessions."),
  component: PracticeHub,
});

const CARDS = [
  { icon: Sparkles, title: "For You", sub: "Based on your weak topics", meta: "Trigonometry · Calculus", tone: "bg-primary text-primary-foreground", big: true },
  { icon: BookOpen, title: "Lesson Practice", sub: "Quadratic Equations", meta: "10 questions", tone: "bg-t-mint/15 text-t-mint" },
  { icon: RotateCcw, title: "Review Mistakes", sub: "Retry what tripped you up", meta: "6 to review", tone: "bg-t-coral/15 text-t-coral" },
  { icon: Zap, title: "Quick Practice", sub: "Five questions, two minutes", meta: "5 questions", tone: "bg-t-sun/20 text-foreground" },
];

function Chips<T extends string | number>({ label, opts, value, onChange, fmt = String }: { label: string; opts: T[]; value: T; onChange: (v: T) => void; fmt?: (v: T) => string }) {
  return (
    <div><p className="mb-2 font-display text-sm font-bold text-muted-foreground">{label}</p>
      <div className="flex flex-wrap gap-2">{opts.map((o) => (
        <button key={o} onClick={() => onChange(o)} className={cn("rounded-full px-4 py-2 font-display text-sm font-bold transition-colors", o === value ? "bg-primary text-primary-foreground" : "bg-muted hover:text-primary")}>{fmt(o)}</button>
      ))}</div></div>
  );
}

function PracticeHub() {
  const [grade, setGrade] = useState(12), [topic, setTopic] = useState("Algebra"), [diff, setDiff] = useState("Medium"), [n, setN] = useState(10);
  return (
    <>
      <PageHeader title={<>Practice what <span className="text-primary">matters.</span></>} sub="Short, focused sessions that adapt to you." />
      <div className="grid gap-5 md:grid-cols-3">
        {CARDS.map(({ icon: Icon, title, sub, meta, tone, big }, i) => (
          <Reveal key={title} delay={i * 60} className={cn(big && "md:row-span-2")}>
            <Link to="/app/quiz" className={cn("group card-lift flex h-full flex-col rounded-[2rem] p-7 shadow-soft", big ? "bg-primary text-primary-foreground" : "border border-border bg-card")}>
              <span className={cn("grid h-14 w-14 place-items-center rounded-2xl", big ? "bg-primary-foreground/15" : tone)}><Icon className="h-6 w-6" /></span>
              <h3 className={cn("mt-6 font-black", big ? "text-4xl" : "text-2xl")}>{title}</h3>
              <p className={cn("mt-1", big ? "opacity-80" : "text-muted-foreground")}>{sub}</p>
              {big && <p aria-hidden className="mt-auto pt-10 font-display text-7xl font-black opacity-15">sin θ</p>}
              <div className="mt-6 flex items-center justify-between font-display font-extrabold"><span className={cn(!big && "text-sm text-muted-foreground")}>{meta}</span><ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" /></div>
            </Link>
          </Reveal>
        ))}
      </div>
      <Reveal className="mt-10 rounded-[2rem] bg-primary-soft p-7 md:p-9">
        <h2 className="flex items-center gap-3 text-2xl font-black"><SlidersHorizontal className="h-6 w-6 text-primary" />Custom Practice</h2>
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          <Chips label="Grade" opts={GRADES.slice(6)} value={grade} onChange={setGrade} fmt={(g) => `G${g}`} />
          <Chips label="Topic" opts={["Algebra", "Functions", "Geometry", "Calculus", "Trigonometry"]} value={topic} onChange={setTopic} />
          <Chips label="Difficulty" opts={["Easy", "Medium", "Hard"]} value={diff} onChange={setDiff} />
          <Chips label="Questions" opts={[5, 10, 20]} value={n} onChange={setN} />
        </div>
        <button onClick={() => toast.success(`Cooking ${n} ${diff.toLowerCase()} ${topic} questions for Grade ${grade}`)} className={cn(mcButton(), "mt-8")}>Start practice <ArrowRight className="h-4 w-4" /></button>
      </Reveal>
    </>
  );
}
