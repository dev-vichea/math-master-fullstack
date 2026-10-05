import { createFileRoute } from "@tanstack/react-router";
import { ArrowUpRight, Search } from "lucide-react";
import { useMemo, useState } from "react";
import { Reveal } from "@/components/mathcook/primitives";
import { PageHeader, topicMeta } from "@/components/app/shared";
import { LIBRARY, LIBRARY_TYPES } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/library")({
  head: () => pageMeta("Library — MathCook", "Explore lessons, formulas, concepts, worked examples, worksheets and past exams."),
  component: Library,
});

const ICONS: Record<string, string> = { Lessons: "📚", Formulas: "📐", Concepts: "🧠", "Worked Examples": "📝", Worksheets: "📄", "Past Exams": "📋", Saved: "⭐" };
const sel = "rounded-full bg-card px-4 py-2.5 font-display text-sm font-bold ring-1 ring-border outline-none focus:ring-primary";

function Library() {
  const [type, setType] = useState<string>("All");
  const [grade, setGrade] = useState("All");
  const [topic, setTopic] = useState("All");
  const [q, setQ] = useState("");
  const topics = [...new Set(LIBRARY.map((l) => l.topic))];
  const list = useMemo(() => LIBRARY.filter((l) =>
    (type === "All" || l.type === type) && (grade === "All" || String(l.grade) === grade) && (topic === "All" || l.topic === topic) &&
    l.title.toLowerCase().includes(q.toLowerCase())), [type, grade, topic, q]);
  return (
    <>
      <PageHeader title={<>The MathCook <span className="text-primary">Library</span></>} sub="Every formula, concept and example, ready when you need it." />
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
        {LIBRARY_TYPES.map((t) => (
          <button key={t} onClick={() => setType(type === t ? "All" : t)} className={cn("card-lift flex flex-col items-center gap-2 rounded-3xl p-4 font-display text-sm font-bold", type === t ? "bg-primary text-primary-foreground shadow-float" : "border border-border bg-card shadow-soft")}>
            <span className="text-2xl">{ICONS[t]}</span>{t}
          </button>
        ))}
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <label className="flex min-w-60 flex-1 items-center gap-2 rounded-full bg-card px-4 py-2.5 ring-1 ring-border focus-within:ring-primary"><Search className="h-4 w-4 text-muted-foreground" /><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search the library" className="w-full bg-transparent font-semibold outline-none" /></label>
        <select value={grade} onChange={(e) => setGrade(e.target.value)} className={sel} aria-label="Grade"><option>All</option>{Array.from({ length: 12 }, (_, i) => <option key={i} value={i + 1}>Grade {i + 1}</option>)}</select>
        <select value={topic} onChange={(e) => setTopic(e.target.value)} className={sel} aria-label="Topic"><option>All</option>{topics.map((t) => <option key={t}>{t}</option>)}</select>
      </div>
      <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((r, i) => {
          const t = topicMeta(r.topic);
          return (
            <Reveal key={r.title} delay={i * 40}>
              <article className="group card-lift flex h-full cursor-pointer flex-col rounded-3xl border border-border bg-card p-6 shadow-soft">
                <div className="flex items-center justify-between"><span className="rounded-full bg-primary-soft px-3 py-1 font-display text-xs font-black text-primary">{ICONS[r.type]} {r.type}</span><ArrowUpRight className="h-5 w-5 text-muted-foreground transition-colors group-hover:text-primary" /></div>
                <h3 className="mt-4 text-xl font-black">{r.title}</h3>
                <p className="mt-3 flex-1 rounded-2xl bg-muted/60 p-4 font-display font-bold">{r.preview}</p>
                <p className="mt-4 text-sm font-semibold text-muted-foreground"><span className={cn("mr-2 rounded-md px-1.5 py-0.5", t.tone)}>{r.topic}</span>Grade {r.grade}</p>
              </article>
            </Reveal>
          );
        })}
        {!list.length && <p className="col-span-full rounded-3xl bg-primary-soft p-10 text-center font-display font-bold">Nothing on this shelf yet. Try another filter.</p>}
      </div>
    </>
  );
}
