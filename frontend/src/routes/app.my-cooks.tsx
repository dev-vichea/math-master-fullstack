import { createFileRoute } from "@tanstack/react-router";
import { Search, ChefHat } from "lucide-react";
import { useMemo, useState } from "react";
import { COOKS } from "@/lib/mathcook/data";
import { CookCard, EmptyState, PageHeader } from "@/components/app/shared";
import { cn } from "@/lib/utils";

const FILTERS = ["All", "Algebra", "Calculus", "Geometry", "Trigonometry", "Probability", "Statistics"];

export const Route = createFileRoute("/app/my-cooks")({
  head: () => ({
    meta: [
      { title: "My Cooks — MathCook" },
      { name: "description", content: "Your solved math problems, all in one place." },
      { property: "og:title", content: "My Cooks — MathCook" },
      { property: "og:description", content: "Your solved math problems, all in one place." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: MyCooks,
});

function MyCooks() {
  const [filter, setFilter] = useState("All");
  const [q, setQ] = useState("");
  const list = useMemo(
    () => COOKS.filter((c) => (filter === "All" || c.topic === filter) && (c.problem + c.skill).toLowerCase().includes(q.toLowerCase())),
    [filter, q],
  );
  return (
    <>
      <PageHeader title="My Cooks" sub="Your solved problems, all in one place." />
      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 lg:mx-0 lg:px-0">
          {FILTERS.map((f) => (
            <button key={f} onClick={() => setFilter(f)}
              className={cn("shrink-0 rounded-full px-4 py-2 font-display text-sm font-bold transition-all",
                filter === f ? "bg-primary text-primary-foreground shadow-soft" : "bg-card text-muted-foreground ring-1 ring-border hover:text-primary")}>
              {f}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2 rounded-full bg-card px-4 py-2.5 ring-1 ring-border focus-within:ring-primary lg:w-72">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search your cooks" className="w-full bg-transparent font-semibold outline-none" />
        </label>
      </div>
      {list.length ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{list.map((c) => <CookCard key={c.id} cook={c} />)}</div>
      ) : (
        <EmptyState icon={ChefHat} title="Your kitchen is still empty." sub="Cook your first math problem and it'll appear here." cta="Start Cooking" to="/app" />
      )}
    </>
  );
}
