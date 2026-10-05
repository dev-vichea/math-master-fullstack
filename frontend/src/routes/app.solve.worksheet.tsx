import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, ArrowRight, Check, Pencil, Sparkles, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { topicMeta } from "@/components/app/shared";
import { WORKSHEET } from "@/lib/mathcook/curriculum";
import { pageMeta } from "@/lib/mathcook/meta";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/solve/worksheet")({
  head: () => pageMeta("Worksheet — MathCook", "Review every problem MathCook found on your worksheet and solve them one by one or all at once."),
  component: WorksheetProblems,
});

function WorksheetProblems() {
  const [items, setItems] = useState(WORKSHEET.map((w, i) => ({ ...w, key: i, solved: false })));
  const [editing, setEditing] = useState<number | null>(null);
  const [draft, setDraft] = useState("");
  const solveAll = () => { setItems((xs) => xs.map((x) => ({ ...x, solved: true }))); toast.success(`All ${items.length} problems cooked`); };
  return (
    <div>
      <Link to="/app/solve" className="inline-flex items-center gap-2 font-display font-bold text-muted-foreground hover:text-primary"><ArrowLeft className="h-4 w-4" />New cook</Link>
      <Reveal className="mt-6 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div><Eyebrow>Worksheet</Eyebrow><h1 className="mt-4 text-4xl font-black md:text-6xl">We found {items.length} problems</h1>
          <p className="mt-3 text-lg text-muted-foreground">Check them, fix anything we misread, then cook.</p></div>
        <button onClick={solveAll} className={mcButton({ size: "lg" })}><Sparkles className="h-5 w-5" />Solve all</button>
      </Reveal>
      <ol className="mt-10 space-y-4">
        {items.map((p, i) => {
          const t = topicMeta(p.topic);
          return (
            <Reveal as="li" key={p.key} delay={i * 50} className="flex flex-col gap-4 rounded-3xl border border-border bg-card p-5 shadow-soft sm:flex-row sm:items-center md:p-6">
              <span className="font-display text-2xl font-black text-primary/40">{String(i + 1).padStart(2, "0")}</span>
              <span className={cn("hidden h-11 w-11 shrink-0 place-items-center rounded-2xl font-display font-black sm:grid", t.tone)}>{t.glyph}</span>
              <div className="min-w-0 flex-1">
                {editing === p.key ? (
                  <div className="flex gap-2">
                    <input autoFocus value={draft} onChange={(e) => setDraft(e.target.value)} className="min-w-0 flex-1 rounded-xl bg-muted px-3 py-2 font-display font-bold outline-none ring-primary focus:ring-2" />
                    <button aria-label="Save" onClick={() => { setItems((xs) => xs.map((x) => x.key === p.key ? { ...x, text: draft } : x)); setEditing(null); }} className="rounded-xl bg-primary p-2 text-primary-foreground"><Check className="h-4 w-4" /></button>
                    <button aria-label="Cancel" onClick={() => setEditing(null)} className="rounded-xl bg-muted p-2"><X className="h-4 w-4" /></button>
                  </div>
                ) : <p className="font-display text-lg font-black">{p.text}</p>}
                <p className="text-sm font-semibold text-muted-foreground">{p.topic} · {p.skill}</p>
              </div>
              <div className="flex items-center gap-2">
                {p.solved && <span className="rounded-full bg-success/15 px-3 py-1 text-sm font-bold text-success">Cooked ✓</span>}
                <button onClick={() => { setEditing(p.key); setDraft(p.text); }} className={mcButton({ variant: "ghost", size: "sm" })}><Pencil className="h-4 w-4" />Edit</button>
                <Link to="/app/solve/$id" params={{ id: p.id }} className={mcButton({ variant: "soft", size: "sm" })}>{p.solved ? "Review" : "Solve"} <ArrowRight className="h-4 w-4" /></Link>
              </div>
            </Reveal>
          );
        })}
      </ol>
    </div>
  );
}
