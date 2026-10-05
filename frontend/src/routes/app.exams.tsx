import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, ArrowRight, Clock, Flag, HelpCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { PageHeader, ProgressBar } from "@/components/app/shared";
import { EXAMS, QUIZ_QUESTIONS } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/exams")({
  head: () => pageMeta("Exams — MathCook", "Chapter, semester, full-grade and mock exams to prepare for the Cambodian national exam."),
  component: ExamsPage,
});

function ExamsPage() {
  const [exam, setExam] = useState<(typeof EXAMS)[number] | null>(null);
  if (exam) return <ExamView title={exam.title} minutes={exam.minutes} onExit={() => setExam(null)} />;
  return (
    <>
      <PageHeader title="Exams" sub="Focused, timed, and serious. Ready when you are." />
      <div className="space-y-4">
        {EXAMS.map((e, i) => (
          <Reveal key={e.id} delay={i * 60} className="flex flex-col gap-4 rounded-[2rem] border border-border bg-card p-6 shadow-soft sm:flex-row sm:items-center md:p-7">
            <span className="font-display text-4xl font-black text-primary/30">{String(i + 1).padStart(2, "0")}</span>
            <div className="flex-1">
              <p className="font-display text-xs font-black uppercase tracking-[0.14em] text-primary">{e.type}</p>
              <h3 className="mt-1 text-2xl font-black">{e.title}</h3>
              <p className="mt-1 flex gap-4 text-sm font-semibold text-muted-foreground"><span className="inline-flex items-center gap-1"><HelpCircle className="h-3.5 w-3.5" />{e.questions} questions</span><span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{e.minutes} min</span></p>
            </div>
            <button onClick={() => setExam(e)} className={mcButton({ variant: i === 3 ? "primary" : "outline" })}>Start exam <ArrowRight className="h-4 w-4" /></button>
          </Reveal>
        ))}
      </div>
    </>
  );
}

export function ExamView({ title, minutes, onExit }: { title: string; minutes: number; onExit: () => void }) {
  const Q = QUIZ_QUESTIONS;
  const [i, setI] = useState(0);
  const [ans, setAns] = useState<(number | null)[]>(Q.map(() => null));
  const [flags, setFlags] = useState<boolean[]>(Q.map(() => false));
  const [left, setLeft] = useState(minutes * 60);
  const [done, setDone] = useState(false);
  useEffect(() => { if (done) return; const t = setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000); return () => clearInterval(t); }, [done]);
  const fmt = (s: number) => `${Math.floor(s / 3600) ? Math.floor(s / 3600) + ":" : ""}${String(Math.floor((s % 3600) / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  const q = Q[i]!;

  if (done) {
    const correct = ans.filter((a, n) => a === Q[n]!.answer).length;
    const topics = [...new Set(Q.map((x) => x.topic))].map((t) => {
      const qs = Q.map((x, n) => ({ x, n })).filter(({ x }) => x.topic === t);
      return { t, v: Math.round((qs.filter(({ x, n }) => ans[n] === x.answer).length / qs.length) * 100) };
    });
    return (
      <div className="mx-auto max-w-3xl">
        <Reveal className="rounded-[2rem] border border-border bg-card p-10 text-center shadow-soft">
          <Eyebrow>{title}</Eyebrow>
          <p className="mt-5 font-display text-7xl font-black text-primary">{Math.round((correct / Q.length) * 100)}%</p>
          <p className="mt-2 text-muted-foreground">{correct}/{Q.length} correct · time used {fmt(minutes * 60 - left)}</p>
        </Reveal>
        <div className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-soft">
          <h3 className="text-xl font-black">Topic performance</h3>
          <div className="mt-4 space-y-4">{topics.map(({ t, v }) => <div key={t}><div className="mb-1 flex justify-between font-display font-bold"><span>{t}</span><span className={v < 60 ? "text-t-coral" : "text-success"}>{v}%</span></div><ProgressBar value={v} tone={v < 60 ? "bg-t-coral" : "bg-primary"} /></div>)}</div>
        </div>
        <div className="mt-6 rounded-3xl bg-primary-soft p-6"><h3 className="text-xl font-black">Weak areas → study plan</h3>
          <p className="mt-2 text-muted-foreground">We've added {topics.filter((t) => t.v < 60).map((t) => t.t).join(", ") || "a review session"} to next week's plan.</p>
          <div className="mt-5 flex flex-wrap gap-3"><Link to="/app/plan" className={mcButton()}>View study plan <ArrowRight className="h-4 w-4" /></Link><button onClick={onExit} className={mcButton({ variant: "outline" })}>All exams</button></div></div>
      </div>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
      <div>
        <div className="flex items-center justify-between rounded-2xl bg-card px-5 py-3 shadow-soft">
          <button onClick={onExit} className="inline-flex items-center gap-2 font-display font-bold text-muted-foreground"><ArrowLeft className="h-4 w-4" />Leave</button>
          <span className="truncate px-3 font-display font-black">{title}</span>
          <span className={cn("inline-flex items-center gap-2 rounded-full px-3 py-1 font-display font-black tabular-nums", left < 300 ? "bg-destructive/10 text-destructive" : "bg-muted")}><Clock className="h-4 w-4" />{fmt(left)}</span>
        </div>
        <div className="mt-4"><ProgressBar value={(ans.filter((a) => a !== null).length / Q.length) * 100} /></div>
        <div className="mt-6 rounded-[2rem] border border-border bg-card p-7 shadow-soft md:p-10">
          <div className="flex items-center justify-between"><span className="font-display font-black text-muted-foreground">Question {i + 1} of {Q.length}</span>
            <button onClick={() => setFlags((f) => f.map((x, k) => (k === i ? !x : x)))} className={cn(mcButton({ variant: "ghost", size: "sm" }), flags[i] && "text-t-coral")}><Flag className={cn("h-4 w-4", flags[i] && "fill-current")} />{flags[i] ? "Flagged" : "Flag"}</button></div>
          <h2 className="mt-4 text-3xl font-black">{q.q}</h2>
          <div className="mt-8 grid gap-3">{q.choices.map((c, n) => (
            <button key={c} onClick={() => setAns((a) => a.map((x, k) => (k === i ? n : x)))} className={cn("flex items-center gap-4 rounded-2xl px-5 py-4 text-left font-display text-lg font-bold ring-2 transition-all", ans[i] === n ? "bg-primary-soft ring-primary" : "bg-muted/50 ring-transparent hover:ring-border")}>
              <span className="grid h-8 w-8 place-items-center rounded-full bg-card text-sm">{"ABCD"[n]}</span>{c}</button>
          ))}</div>
          <div className="mt-8 flex justify-between">
            <button disabled={i === 0} onClick={() => setI(i - 1)} className={cn(mcButton({ variant: "outline" }), i === 0 && "opacity-40")}>Previous</button>
            {i + 1 < Q.length ? <button onClick={() => setI(i + 1)} className={mcButton()}>Next <ArrowRight className="h-4 w-4" /></button> : <button onClick={() => setDone(true)} className={mcButton()}>Submit exam</button>}
          </div>
        </div>
      </div>
      <aside className="rounded-3xl border border-border bg-card p-5 shadow-soft lg:sticky lg:top-8 lg:self-start">
        <p className="font-display font-black">Questions</p>
        <div className="mt-4 grid grid-cols-5 gap-2">{Q.map((_, n) => (
          <button key={n} onClick={() => setI(n)} className={cn("relative grid aspect-square place-items-center rounded-xl font-display text-sm font-black", n === i ? "bg-primary text-primary-foreground" : ans[n] !== null ? "bg-primary-soft text-primary" : "bg-muted")}>
            {n + 1}{flags[n] && <span className="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-t-coral" />}</button>
        ))}</div>
        <button onClick={() => setDone(true)} className={cn(mcButton({ variant: "soft", size: "sm" }), "mt-5 w-full")}>Submit exam</button>
      </aside>
    </div>
  );
}
