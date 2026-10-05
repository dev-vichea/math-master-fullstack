import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Bookmark, Lightbulb, RotateCcw, Sigma, Sparkles, Star, TriangleAlert } from "lucide-react";
import type { ReactNode } from "react";
import { toast } from "sonner";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { getCook, type Cook, type Step } from "@/lib/mathcook/data";
import { MathView } from "@/components/ui/MathView";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/solve/$id")({
  loader: async ({ params }) => {
    const cook = await getCook(params.id);
    if (!cook) throw notFound();
    return cook;
  },
  head: ({ loaderData }) => {
    const t = loaderData ? `${loaderData.problem} — MathCook Solution` : "Solution — MathCook";
    const d = loaderData ? `Step-by-step ${loaderData.topic.toLowerCase()} solution using ${loaderData.method}.` : "Step-by-step solution.";
    return { meta: [
      { title: t }, { name: "description", content: d },
      { property: "og:title", content: t }, { property: "og:description", content: d },
      { property: "og:type", content: "article" }, { name: "twitter:card", content: "summary_large_image" },
    ] };
  },
  notFoundComponent: () => (
    <div className="py-20 text-center"><h1 className="text-4xl font-black">This cook doesn't exist.</h1>
      <Link to="/app/my-cooks" className={cn(mcButton(), "mt-6")}>Back to My Cooks</Link></div>
  ),
  component: Solver,
});

function SolverHeader({ cook }: { cook: Cook }) {
  return (
    <Reveal>
      <Link to="/app/my-cooks" className="inline-flex items-center gap-2 font-display font-bold text-muted-foreground hover:text-primary"><ArrowLeft className="h-4 w-4" />Back to My Cooks</Link>
      <div className="mt-6"><Eyebrow>{cook.topic} · {cook.skill}</Eyebrow></div>
      <h1 className="mt-4 text-4xl font-black md:text-6xl">Let's cook this one.</h1>
      <div className="mt-6 rounded-[2rem] bg-primary-soft px-6 py-8 text-center md:py-10">
        <div className="font-display text-3xl font-black text-primary md:text-5xl">
          <MathView math={cook.problem} />
        </div>
      </div>
    </Reveal>
  );
}

function UnderstandingPanel({ cook }: { cook: Cook }) {
  const rows = [["Topic", cook.topic], ["Skill", cook.skill], ["Method", cook.method], ["Confidence", cook.confidence]];
  return (
    <Reveal delay={100} className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-soft">
      <p className="flex items-center gap-2 font-display text-sm font-extrabold uppercase tracking-[0.14em] text-primary"><Sparkles className="h-4 w-4" />MathCook understood</p>
      <dl className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        {rows.map(([k, v]) => (
          <div key={k}><dt className="text-sm text-muted-foreground">{k}</dt>
            <dd className={cn("font-display text-lg font-black", k === "Confidence" && "text-success")}>{v}</dd></div>
        ))}
      </dl>
    </Reveal>
  );
}

function SolutionStep({ step, n }: { step: Step; n: number }) {
  return (
    <Reveal delay={n * 120} className="card-lift rounded-3xl border border-border bg-card p-6 shadow-soft md:p-8">
      <p className="font-display text-xs font-black tracking-[0.18em] text-primary">STEP {String(n + 1).padStart(2, "0")}</p>
      <h3 className="mt-2 text-2xl font-black">{step.title}</h3>
      <p className="mt-2 text-muted-foreground whitespace-pre-line">{step.body}</p>
      {step.math && (
        <div className="mt-4 inline-block rounded-2xl bg-muted px-5 py-3 font-display text-xl font-black">
          <MathView math={step.math} />
        </div>
      )}
    </Reveal>
  );
}

function FinalAnswer({ answer }: { answer: string }) {
  return (
    <Reveal className="rounded-[2rem] bg-primary p-8 text-center text-primary-foreground shadow-float md:p-10">
      <Star className="mx-auto h-9 w-9 animate-floaty fill-t-sun text-t-sun" />
      <p className="mt-3 font-display text-xs font-black tracking-[0.2em] opacity-80">FINAL ANSWER</p>
      <div className="mt-3 font-display text-3xl font-black md:text-4xl">
        <MathView math={answer} />
      </div>
    </Reveal>
  );
}

function SideCard({ icon, title, tone, children }: { icon: ReactNode; title: string; tone: string; children: ReactNode }) {
  return (
    <div className="rounded-3xl border border-border bg-card p-6 shadow-soft">
      <span className={cn("grid h-10 w-10 place-items-center rounded-2xl", tone)}>{icon}</span>
      <h3 className="mt-4 text-xl font-black">{title}</h3>
      <div className="mt-2 text-muted-foreground">{children}</div>
    </div>
  );
}
const WhyThisMethod = ({ text }: { text: string }) => <SideCard icon={<Lightbulb className="h-5 w-5" />} title="Why this method?" tone="bg-primary-soft text-primary"><p className="whitespace-pre-line">{text}</p></SideCard>;
const Formula = ({ text }: { text: string }) => <SideCard icon={<Sigma className="h-5 w-5" />} title="Formula" tone="bg-t-sky/15 text-t-sky"><div className="rounded-2xl bg-muted p-4 font-display font-bold text-foreground"><MathView math={text} /></div></SideCard>;
const CommonMistake = ({ text }: { text: string }) => <SideCard icon={<TriangleAlert className="h-5 w-5" />} title="Common mistake" tone="bg-t-coral/15 text-t-coral"><p className="whitespace-pre-line">{text}</p></SideCard>;

function Solver() {
  const cook = Route.useLoaderData();
  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
      <div>
        <SolverHeader cook={cook} />
        <UnderstandingPanel cook={cook} />
        <div className="mt-10 space-y-5">{cook.steps.map((s, i) => <SolutionStep key={i} step={s} n={i} />)}</div>
        <div className="mt-8"><FinalAnswer answer={cook.answer} /></div>
        <div className="mt-8 flex flex-wrap gap-3">
          <button onClick={() => toast.success("Saved to My Cooks")} className={mcButton()}><Bookmark className="h-4 w-4" />Save Cook</button>
          <Link to="/app" className={mcButton({ variant: "outline" })}><RotateCcw className="h-4 w-4" />Try Another Problem</Link>
          <Link to="/app/learn" className={mcButton({ variant: "soft" })}><Sparkles className="h-4 w-4" />Practice Similar</Link>
        </div>
      </div>
      <aside className="space-y-5 lg:sticky lg:top-28 lg:self-start">
        <WhyThisMethod text={cook.why} />
        <Formula text={cook.formula} />
        <CommonMistake text={cook.mistake} />
      </aside>
    </div>
  );
}
