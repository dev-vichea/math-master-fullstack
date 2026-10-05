import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, LogOut } from "lucide-react";
import { mcButton } from "@/components/mathcook/primitives";
import { PageHeader } from "@/components/app/shared";
import { USER } from "@/lib/mathcook/data";
import { pageMeta } from "@/lib/mathcook/meta";

export const Route = createFileRoute("/app/settings")({
  head: () => pageMeta("Settings — MathCook", "Manage your MathCook profile, grade and study preferences."),
  component: Settings,
});

function Settings() {
  const rows = [["Name", USER.name], ["Email", USER.email], ["Grade", "Grade 12"], ["Daily goal", "20 minutes"], ["Focus", "Calculus, Exam Preparation"]];
  return (
    <div className="max-w-2xl">
      <PageHeader title="Settings" sub="Your profile and study preferences." />
      <div className="divide-y divide-border rounded-[2rem] border border-border bg-card shadow-soft">
        {rows.map(([k, v]) => <div key={k} className="flex justify-between gap-4 p-5"><span className="font-semibold text-muted-foreground">{k}</span><span className="text-right font-display font-bold">{v}</span></div>)}
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/onboarding" className={mcButton()}>Redo onboarding <ArrowRight className="h-4 w-4" /></Link>
        <Link to="/" className={mcButton({ variant: "outline" })}><LogOut className="h-4 w-4" />Log out</Link>
      </div>
    </div>
  );
}
