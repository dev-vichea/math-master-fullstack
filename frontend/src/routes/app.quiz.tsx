import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Clock, HelpCircle, Lightbulb, RotateCcw, Check, X } from "lucide-react";
import { useState } from "react";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { PageHeader } from "@/components/app/shared";
import { QUIZZES, QUIZ_QUESTIONS } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/quiz")({
  head: () => pageMeta("Quiz — MathCook", "Lesson, chapter, topic and quick quizzes with instant feedback and recommended practice."),
  component: QuizPage,
});

function QuizPage() {
  const [active, setActive] = useState<(typeof QUIZZES)[number] | null>(null);
  if (active) return <QuizView title={active.title} onExit={() => setActive(null)} />;
  return (
    <>
      <PageHeader title={<>Quiz <span className="text-primary">time.</span></>} sub="Check what stuck. Every result feeds your study plan." />
      <div className="grid gap-5 sm:grid-cols-2">
        {QUIZZES.map((q, i) => (
          <Reveal key={q.id} delay={i * 60}>
            <button onClick={() => setActive(q)} className="group card-lift flex w-full items-center gap-5 rounded-[2rem] border border-border bg-card p-6 text-left shadow-soft">
              <span className="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-primary-soft font-display text-xl font-black text-primary">{q.glyph}</span>
              <div className="flex-1">
                <p className="font-display text-xs font-black uppercase tracking-[0.14em] text-primary">{q.type}</p>
                <h3 className="mt-1 text-xl font-black">{q.title}</h3>
                <p className="mt-1 flex gap-3 text-sm font-semibold text-muted-foreground"><span className="inline-flex items-center gap-1"><HelpCircle className="h-3.5 w-3.5" />{q.questions} questions</span><span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{q.minutes} min</span></p>
              </div>
              <ArrowRight className="h-5 w-5 text-primary transition-transform group-hover:translate-x-1" />
            </button>
          </Reveal>
        ))}
      </div>
    </>
  );
}

export function QuizView({ title, onExit }: { title: string; onExit: () => void }) {
  const Q = QUIZ_QUESTIONS;
  const [i, setI] = useState(0);
  const [answers, setAnswers] = useState<(number | null)[]>(Q.map(() => null));
  const [hint, setHint] = useState(false);
  const [done, setDone] = useState(false);
  const q = Q[i]!;
  const picked = answers[i];

  if (done) {
    const correct = answers.filter((a, n) => a === Q[n]!.answer).length;
    const wrong = Q.filter((x, n) => answers[n] !== x.answer);
    const weak = [...new Set(wrong.map((w) => w.topic))];
    return (
      <div className="mx-auto max-w-3xl">
        <Reveal className="rounded-[2rem] bg-primary p-10 text-center text-primary-foreground shadow-float">
          <p className="font-display text-xs font-black uppercase tracking-[0.2em] opacity-80">{title}</p>
          <p className="mt-4 font-display text-7xl font-black">{Math.round((correct / Q.length) * 100)}%</p>
          <p className="mt-2 text-lg opacity-90">{correct} of {Q.length} correct</p>
        </Reveal>
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <div className="rounded-3xl border border-border bg-card p-6 shadow-soft"><h3 className="text-xl font-black">Weak topics</h3>
            <div className="mt-3 flex flex-wrap gap-2">{weak.length ? weak.map((w) => <span key={w} className="rounded-full bg-t-coral/15 px-3 py-1 text-sm font-bold text-t-coral">{w}</span>) : <span className="text-muted-foreground">None, perfect cook! ⭐</span>}</div></div>
          <div className="rounded-3xl border border-border bg-card p-6 shadow-soft"><h3 className="text-xl font-black">Mistakes</h3>
            <ul className="mt-3 space-y-2 text-sm">{wrong.length ? wrong.map((w) => <li key={w.q}><b>{w.q}</b> → {w.choices[w.answer]}</li>) : <li className="text-muted-foreground">No mistakes.</li>}</ul></div>
        </div>
        <div className="mt-6 rounded-3xl bg-primary-soft p-6"><Eyebrow>Recommended practice</Eyebrow>
          <p className="mt-3 font-display text-lg font-bold">{weak.length ? `10 questions on ${weak.join(" & ")}` : "Move on to the Checkpoint in your journey"}</p>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link to="/app/practice" className={mcButton()}>Practice now <ArrowRight className="h-4 w-4" /></Link>
            <Link to="/app/learn" className={mcButton({ variant: "outline" })}>Back to journey</Link>
            <button onClick={onExit} className={mcButton({ variant: "ghost" })}><RotateCcw className="h-4 w-4" />Other quizzes</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <div className="flex items-center justify-between">
        <button onClick={onExit} className="font-display font-bold text-muted-foreground hover:text-primary">✕ Exit</button>
        <span className="font-display font-black">Question {i + 1} / {Q.length}</span>
      </div>
      <div className="mt-4 flex gap-1.5">{Q.map((_, n) => <span key={n} className={cn("h-2 flex-1 rounded-full transition-colors", n < i ? "bg-primary" : n === i ? "bg-primary/50" : "bg-muted")} />)}</div>
      <div key={i} className="mt-10 animate-fade-in rounded-[2rem] border border-border bg-card p-7 shadow-soft md:p-10">
        <p className="font-display text-xs font-black uppercase tracking-[0.16em] text-primary">{title}</p>
        <h2 className="mt-3 text-3xl font-black md:text-4xl">{q.q}</h2>
        <div className="mt-8 grid gap-3">
          {q.choices.map((c, n) => {
            const show = picked !== null, isRight = n === q.answer, isPicked = n === picked;
            return (
              <button key={c} disabled={show} onClick={() => setAnswers((a) => a.map((x, k) => (k === i ? n : x)))}
                className={cn("flex items-center gap-4 rounded-2xl px-5 py-4 text-left font-display text-lg font-bold ring-2 transition-all",
                  !show && "bg-muted/60 ring-transparent hover:bg-primary-soft hover:ring-primary",
                  show && isRight && "bg-success/10 ring-success", show && isPicked && !isRight && "bg-destructive/10 ring-destructive",
                  show && !isRight && !isPicked && "bg-muted/40 opacity-60 ring-transparent")}>
                <span className="grid h-8 w-8 place-items-center rounded-full bg-card text-sm">{"ABCD"[n]}</span><span className="flex-1">{c}</span>
                {show && isRight && <Check className="h-5 w-5 text-success" />}{show && isPicked && !isRight && <X className="h-5 w-5 text-destructive" />}
              </button>
            );
          })}
        </div>
        {hint && <p className="mt-5 rounded-2xl bg-t-sun/15 p-4 font-semibold">💡 {q.hint}</p>}
        <div className="mt-8 flex items-center justify-between">
          <button onClick={() => setHint(true)} className={mcButton({ variant: "ghost", size: "sm" })}><Lightbulb className="h-4 w-4" />Hint</button>
          <button disabled={picked === null} onClick={() => { setHint(false); i + 1 < Q.length ? setI(i + 1) : setDone(true); }} className={cn(mcButton(), picked === null && "pointer-events-none opacity-40")}>
            {i + 1 < Q.length ? "Next" : "Finish"} <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
