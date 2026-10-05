import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, ArrowRight } from "lucide-react";
import { Reveal, mcButton } from "@/components/mathcook/primitives";
import { PageHeader, ProgressBar } from "@/components/app/shared";
import { PLAN } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/plan")({
  head: () => pageMeta("Study Plan — MathCook", "Your personalized 30-day math plan with weekly goals and daily lessons, practice and quizzes."),
  component: StudyPlan,
});

const KIND_TONE: Record<string, string> = { Lesson: "bg-primary-soft text-primary", Practice: "bg-t-mint/15 text-t-mint", Quiz: "bg-t-sky/15 text-t-sky", Review: "bg-t-coral/15 text-t-coral", Rest: "bg-muted text-muted-foreground" };

function StudyPlan() {
  return (
    <>
      <PageHeader title={PLAN.title} sub="Built from your grade, goals and recent results.">
        <div className="mt-6 flex max-w-xl items-center gap-4"><ProgressBar value={PLAN.progress} /><span className="font-display font-black text-primary">{PLAN.progress}%</span></div>
      </PageHeader>
      <Reveal className="rounded-[2rem] border border-border bg-card p-6 shadow-soft">
        <h2 className="text-xl font-black">This week</h2>
        <div className="mt-5 grid grid-cols-7 gap-2">
          {PLAN.days.map((d) => (
            <div key={d.d} className={cn("flex flex-col items-center gap-2 rounded-2xl p-2 py-4 text-center transition-all md:p-4", d.today ? "bg-primary text-primary-foreground shadow-float" : "bg-muted/50")}>
              <span className="font-display text-xs font-black uppercase">{d.d}</span>
              {d.done ? <span className="grid h-8 w-8 place-items-center rounded-full bg-success text-primary-foreground"><Check className="h-4 w-4" /></span> : <span className={cn("h-8 w-8 rounded-full border-2 border-dashed", d.today ? "border-primary-foreground" : "border-border")} />}
              <span className={cn("hidden rounded-full px-2 py-0.5 text-[11px] font-bold sm:inline", d.today ? "bg-primary-foreground/20" : KIND_TONE[d.kind])}>{d.kind}</span>
            </div>
          ))}
        </div>
        <Link to="/app/learn" className={cn(mcButton({ size: "sm" }), "mt-6")}>Start today's lesson <ArrowRight className="h-4 w-4" /></Link>
      </Reveal>
      <div className="relative mt-12">
        <div aria-hidden className="absolute bottom-0 left-6 top-0 border-l-4 border-dashed border-primary/20" />
        <div className="space-y-6">
          {PLAN.weeks.map((w, i) => (
            <Reveal key={w.week} delay={i * 80} className="relative pl-16">
              <span className="absolute left-0 top-2 grid h-12 w-12 place-items-center rounded-2xl bg-primary font-display font-black text-primary-foreground ring-8 ring-background">W{w.week}</span>
              <div className="rounded-3xl border border-border bg-card p-6 shadow-soft">
                <h3 className="text-xl font-black">Week {w.week}</h3>
                <ul className="mt-3 space-y-2">{w.items.map((it) => (
                  <li key={it.t} className={cn("flex items-center gap-3 rounded-2xl px-3 py-2 font-display font-bold", it.s === "current" && "bg-primary-soft text-primary", it.s === "done" && "text-muted-foreground")}>
                    {it.s === "done" ? <Check className="h-5 w-5 text-success" /> : <ArrowRight className="h-5 w-5" />}{it.t}{it.s === "current" && <span className="ml-auto text-xs uppercase tracking-wider">Now</span>}
                  </li>))}</ul>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </>
  );
}
