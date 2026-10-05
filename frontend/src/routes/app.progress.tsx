import { createFileRoute } from "@tanstack/react-router";
import { Reveal } from "@/components/mathcook/primitives";
import { PageHeader, ProgressBar } from "@/components/app/shared";
import { ACHIEVEMENTS, SKILL_MASTERY, STATS } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { useAnimated } from "@/components/app/shared";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/progress")({
  head: () => pageMeta("Progress — MathCook", "Your mastery, streak, solved problems, quiz and exam performance, and achievements."),
  component: ProgressDashboard,
});

function Bar({ value, tone }: { value: number; tone: string }) { return <ProgressBar value={useAnimated(value)} tone={tone} />; }

function ProgressDashboard() {
  const [hero, ...rest] = STATS;
  return (
    <>
      <PageHeader title={<>Look how far you've <span className="text-primary">cooked.</span></>} sub="Every problem, lesson and quiz adds up." />
      <div className="grid gap-4 md:grid-cols-4">
        <Reveal className="relative overflow-hidden rounded-[2rem] bg-primary p-7 text-primary-foreground shadow-float md:row-span-2">
          <span aria-hidden className="absolute -bottom-6 -right-2 font-display text-[8rem] font-black opacity-10">∞</span>
          <p className="font-display text-sm font-bold opacity-80">{hero!.label}</p><p className="mt-2 font-display text-6xl font-black">{hero!.value}</p>
        </Reveal>
        {rest.map((s, i) => (
          <Reveal key={s.label} delay={i * 50} className="rounded-3xl border border-border bg-card p-5 shadow-soft">
            <p className="text-sm font-semibold text-muted-foreground">{s.label}</p><p className="mt-1 font-display text-3xl font-black">{s.value}</p>
          </Reveal>
        ))}
      </div>
      <Reveal className="mt-10 rounded-[2rem] border border-border bg-card p-7 shadow-soft">
        <h2 className="text-2xl font-black">Subject mastery</h2>
        <div className="mt-6 space-y-5">{SKILL_MASTERY.map((s) => (
          <div key={s.name}><div className="mb-2 flex justify-between font-display font-bold"><span>{s.glyph} · {s.name}</span><span>{s.value}%</span></div><Bar value={s.value} tone={s.tone} /></div>
        ))}</div>
      </Reveal>
      <h2 className="mb-5 mt-12 text-2xl font-black">Achievements</h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {ACHIEVEMENTS.map((a, i) => (
          <Reveal key={a.title} delay={i * 60} className={cn("card-lift flex flex-col items-center rounded-3xl p-6 text-center", a.earned ? "border border-border bg-card shadow-soft" : "bg-muted/50 opacity-60 grayscale")}>
            <span className="grid h-16 w-16 place-items-center rounded-full bg-primary-soft text-3xl">{a.icon}</span>
            <p className="mt-3 font-display font-black">{a.title}</p><p className="text-xs font-semibold text-muted-foreground">{a.earned ? "Earned" : "Locked"}</p>
          </Reveal>
        ))}
      </div>
    </>
  );
}
