import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, ArrowRight, Check, Lightbulb, X } from "lucide-react";
import { useState } from "react";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/learn/$lessonId")({
  head: () => pageMeta("Quadratic Equations — MathCook Lesson", "Learn what a quadratic equation is, see a worked example and try it yourself."),
  component: LessonView,
});

const STEPS = [
  ["Look for two numbers", "Product = 6, sum = -5 → -2 and -3"],
  ["Factor", "(x - 2)(x - 3) = 0"],
  ["Zero product rule", "x - 2 = 0 or x - 3 = 0"],
  ["Answer", "x = 2 or x = 3"],
];

function LessonView() {
  const [pick, setPick] = useState<number | null>(null);
  const choices = ["x = 3, 4", "x = -3, -4", "x = 2, 6", "x = 1, 12"];
  return (
    <article className="mx-auto max-w-3xl">
      <Link to="/app/learn" className="inline-flex items-center gap-2 font-display font-bold text-muted-foreground hover:text-primary"><ArrowLeft className="h-4 w-4" />Back to journey</Link>
      <Reveal className="mt-6"><Eyebrow>Lesson 04 · Algebra</Eyebrow><h1 className="mt-4 text-4xl font-black md:text-6xl">Quadratic Equations</h1></Reveal>
      <div className="mt-6 h-2 overflow-hidden rounded-full bg-muted"><div className="h-full w-3/5 rounded-full bg-primary" /></div>

      <Reveal as="section" className="mt-12">
        <h2 className="text-2xl font-black md:text-3xl">What is a quadratic equation?</h2>
        <p className="mt-4 text-lg leading-relaxed text-muted-foreground">A quadratic equation is any equation where the highest power of x is 2. It always fits the shape:</p>
        <p className="mt-5 rounded-3xl bg-primary-soft p-6 text-center font-display text-3xl font-black text-primary">ax² + bx + c = 0</p>
        <p className="mt-4 text-lg leading-relaxed text-muted-foreground">Its graph is a parabola, and the <b className="text-foreground">solutions</b> are where that curve crosses the x-axis. Most have two solutions.</p>
      </Reveal>

      <Reveal as="section" className="mt-12">
        <h2 className="text-2xl font-black md:text-3xl">Example</h2>
        <p className="mt-4 rounded-3xl border border-border bg-card p-6 text-center font-display text-3xl font-black shadow-soft">x² - 5x + 6 = 0</p>
        <ol className="mt-5 space-y-3">
          {STEPS.map(([t, m], i) => (
            <Reveal as="li" key={t} delay={i * 100} className="flex gap-4 rounded-3xl bg-card p-5 shadow-soft">
              <span className="font-display text-sm font-black text-primary">{String(i + 1).padStart(2, "0")}</span>
              <div><p className="font-display font-black">{t}</p><p className="mt-1 font-display text-lg font-bold text-muted-foreground">{m}</p></div>
            </Reveal>
          ))}
        </ol>
      </Reveal>

      <Reveal as="section" className="mt-12 rounded-[2rem] bg-primary-soft p-6 md:p-8">
        <p className="flex items-center gap-2 font-display text-xs font-black uppercase tracking-[0.16em] text-primary"><Lightbulb className="h-4 w-4" />Try it yourself</p>
        <h3 className="mt-3 text-2xl font-black">Solve x² - 7x + 12 = 0</h3>
        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {choices.map((c, i) => {
            const chosen = pick === i, right = i === 0;
            return (
              <button key={c} onClick={() => setPick(i)} disabled={pick !== null && pick === 0}
                className={cn("flex items-center justify-between rounded-2xl bg-card px-5 py-4 text-left font-display text-lg font-bold ring-2 transition-all",
                  chosen ? (right ? "ring-success" : "ring-destructive") : "ring-transparent hover:ring-primary")}>
                {c}{chosen && (right ? <Check className="h-5 w-5 text-success" /> : <X className="h-5 w-5 text-destructive" />)}
              </button>
            );
          })}
        </div>
        {pick !== null && <p className={cn("mt-4 font-semibold", pick === 0 ? "text-success" : "text-destructive")}>{pick === 0 ? "Nailed it! 3 × 4 = 12 and 3 + 4 = 7." : "Not quite. Which two numbers multiply to 12 and add to 7?"}</p>}
      </Reveal>

      <div className="mt-10 flex flex-wrap gap-3">
        <Link to="/app/practice" className={mcButton({ variant: "outline" })}>Practice this concept <ArrowRight className="h-4 w-4" /></Link>
        <Link to="/app/learn" className={mcButton()}>Continue to next lesson <ArrowRight className="h-4 w-4" /></Link>
      </div>
    </article>
  );
}
