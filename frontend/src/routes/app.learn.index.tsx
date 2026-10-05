import { createFileRoute, Link } from "@tanstack/react-router";
import { Check, Clock, Lock, Trophy, FlaskConical, Flag, Play } from "lucide-react";
import { useState } from "react";
import { Reveal } from "@/components/mathcook/primitives";
import { PageHeader } from "@/components/app/shared";
import { CHAPTERS, GRADES, STUDENT, type Chapter, type Lesson } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/learn/")({
  head: () => pageMeta("Learn — MathCook Curriculum", "Follow your Grade 1–12 math journey chapter by chapter, from lessons to mastery."),
  component: Learn,
});

export function CurriculumSelector({ grade, onChange }: { grade: number; onChange: (g: number) => void }) {
  return (
    <div className="no-scrollbar -mx-4 flex snap-x items-center gap-3 overflow-x-auto px-4 pb-4 pt-2 md:mx-0 md:flex-wrap md:overflow-visible md:px-0">
      {GRADES.map((g) => {
        const active = g === grade;
        return (
          <button key={g} onClick={() => onChange(g)}
            className={cn(
              "relative snap-center shrink-0 rounded-[1.5rem] px-5 py-2.5 transition-all duration-200",
              active
                ? "-translate-y-1 bg-primary px-7 text-primary-foreground shadow-[0_6px_0_0_var(--primary-deep)]"
                : "border-2 border-b-4 border-border bg-card text-primary hover:border-primary active:translate-y-0.5 active:border-b-2",
            )}>
            {active && <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full border-2 border-background bg-t-sun" />}
            <span className={cn("block text-sm font-bold leading-none", active ? "opacity-90" : "opacity-70")}>Grade</span>
            <span className="font-display text-2xl font-black leading-none">{g}</span>
          </button>
        );
      })}
    </div>
  );
}

const kindIcon = { lesson: Play, practice: FlaskConical, checkpoint: Flag, mastery: Trophy };

export function LessonCard({ lesson, side }: { lesson: Lesson; side: "left" | "right" }) {
  const Icon = lesson.state === "done" ? Check : lesson.state === "locked" ? Lock : kindIcon[lesson.kind];
  const node = (
    <span className={cn("relative z-10 grid h-14 w-14 shrink-0 place-items-center rounded-full font-display ring-8 ring-background transition-transform",
      lesson.state === "done" && "bg-success text-primary-foreground",
      lesson.state === "current" && "animate-floaty bg-primary text-primary-foreground shadow-float",
      lesson.state === "locked" && "bg-muted text-muted-foreground",
      lesson.kind === "mastery" && lesson.state === "locked" && "bg-t-sun/25 text-foreground")}>
      <Icon className="h-6 w-6" />
    </span>
  );
  const body = (
    <div className={cn("w-full max-w-sm rounded-3xl border bg-card p-5 shadow-soft transition-all",
      lesson.state === "current" ? "border-primary card-lift" : "border-border", lesson.state === "locked" && "opacity-70")}>
      <p className="font-display text-xs font-black uppercase tracking-[0.14em] text-primary">{lesson.kind}</p>
      <h3 className="mt-1 text-xl font-black">{lesson.title}</h3>
      <div className="mt-3 flex flex-wrap gap-3 text-sm font-semibold text-muted-foreground">
        <span>{lesson.difficulty}</span><span className="inline-flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{lesson.minutes} min</span>
        {lesson.state !== "locked" && <span className="text-primary">{lesson.progress}%</span>}
      </div>
      {lesson.state !== "locked" && <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted"><div className="h-full rounded-full bg-primary" style={{ width: `${lesson.progress}%` }} /></div>}
    </div>
  );
  const inner = (
    <div className={cn("flex items-center gap-5 md:w-1/2", side === "right" ? "md:ml-auto md:pl-0" : "md:flex-row-reverse md:text-right md:[&>div]:ml-auto")}>
      <div className="md:-mx-7">{node}</div>{body}
    </div>
  );
  return lesson.state === "locked" ? inner : <Link to="/app/learn/$lessonId" params={{ lessonId: lesson.id }} className="block">{inner}</Link>;
}

export function LearningJourney({ chapter }: { chapter: Chapter }) {
  return (
    <section className="mt-14">
      <Reveal className="flex items-center gap-4">
        <span className="grid h-14 w-14 place-items-center rounded-2xl bg-primary-soft font-display text-xl font-black text-primary">{chapter.glyph}</span>
        <div><p className="font-display text-xs font-black uppercase tracking-[0.16em] text-muted-foreground">Chapter</p><h2 className="text-3xl font-black">{chapter.title}</h2></div>
      </Reveal>
      <div className="relative mt-8">
        <div aria-hidden className="absolute bottom-6 left-7 top-6 w-0 border-l-4 border-dashed border-primary/25 md:left-1/2" />
        <div className="space-y-6">
          {chapter.lessons.map((l, i) => <Reveal key={l.id} delay={i * 70}><LessonCard lesson={l} side={i % 2 ? "left" : "right"} /></Reveal>)}
        </div>
      </div>
    </section>
  );
}

function Learn() {
  const [grade, setGrade] = useState(STUDENT.grade);
  return (
    <>
      <PageHeader title={<>Grade {grade} <span className="text-primary">Mathematics</span></>} sub="Chapter → Lessons → Practice → Checkpoint → Mastery. One recipe at a time." />
      <CurriculumSelector grade={grade} onChange={setGrade} />
      {grade === 12 ? CHAPTERS.map((c) => <LearningJourney key={c.id} chapter={c} />) : (
        <div className="mt-12 rounded-[2rem] bg-primary-soft p-10 text-center">
          <p className="font-display text-5xl font-black text-primary/40">Grade {grade}</p>
          <h3 className="mt-3 text-2xl font-black">This kitchen is being stocked.</h3>
          <p className="mt-2 text-muted-foreground">Grade {grade} chapters will appear here soon.</p>
        </div>
      )}
    </>
  );
}
