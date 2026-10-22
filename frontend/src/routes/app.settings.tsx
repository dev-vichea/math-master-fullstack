import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Check, Globe, LogOut } from "lucide-react";
import { mcButton } from "@/components/mathcook/primitives";
import { PageHeader } from "@/components/app/shared";
import { USER } from "@/lib/mathcook/data";
import { pageMeta } from "@/lib/mathcook/meta";
import { useLanguage } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/app/settings")({
  head: () => pageMeta("Settings — MathCook", "Manage your MathCook profile, grade and study preferences."),
  component: Settings,
});

function Settings() {
  const { language, setLanguage, t } = useLanguage();

  const rows = [
    [t("settingsName"), USER.name],
    [t("settingsEmail"), USER.email],
    [t("settingsGrade"), "Grade 12"],
    [t("settingsDailyGoal"), "20 minutes"],
    [t("settingsFocus"), "Calculus, Exam Preparation"],
  ];

  return (
    <div className="max-w-2xl space-y-8">
      <PageHeader title={t("settingsTitle")} sub={t("settingsSub")} />

      {/* Language Selection Card */}
      <div className="rounded-[2rem] border border-border bg-card p-6 shadow-soft md:p-8">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-2xl bg-primary-soft text-primary">
            <Globe className="h-5 w-5" />
          </span>
          <div>
            <h2 className="font-display text-lg font-bold text-foreground">{t("settingsLanguage")}</h2>
            <p className="text-xs text-muted-foreground">{t("settingsLanguageSub")}</p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {/* Khmer option */}
          <button
            type="button"
            onClick={() => setLanguage("km")}
            className={cn(
              "group relative flex items-center justify-between rounded-2xl border-2 p-4 text-left transition-all duration-200",
              language === "km"
                ? "border-primary bg-primary-soft/40 shadow-xs"
                : "border-border hover:border-border/80 hover:bg-muted/40"
            )}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🇰🇭</span>
              <div>
                <p className="font-display font-bold text-foreground">ភាសាខ្មែរ</p>
                <p className="text-xs text-muted-foreground">Khmer (កម្ពុជា)</p>
              </div>
            </div>
            {language === "km" && (
              <span className="grid h-6 w-6 place-items-center rounded-full bg-primary text-primary-foreground">
                <Check className="h-3.5 w-3.5 stroke-[3]" />
              </span>
            )}
          </button>

          {/* English option */}
          <button
            type="button"
            onClick={() => setLanguage("en")}
            className={cn(
              "group relative flex items-center justify-between rounded-2xl border-2 p-4 text-left transition-all duration-200",
              language === "en"
                ? "border-primary bg-primary-soft/40 shadow-xs"
                : "border-border hover:border-border/80 hover:bg-muted/40"
            )}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🇬🇧</span>
              <div>
                <p className="font-display font-bold text-foreground">English</p>
                <p className="text-xs text-muted-foreground">International (US/UK)</p>
              </div>
            </div>
            {language === "en" && (
              <span className="grid h-6 w-6 place-items-center rounded-full bg-primary text-primary-foreground">
                <Check className="h-3.5 w-3.5 stroke-[3]" />
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Profile Details */}
      <div className="divide-y divide-border rounded-[2rem] border border-border bg-card shadow-soft">
        {rows.map(([k, v]) => (
          <div key={k} className="flex justify-between gap-4 p-5">
            <span className="font-semibold text-muted-foreground">{k}</span>
            <span className="text-right font-display font-bold">{v}</span>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <Link to="/onboarding" className={mcButton()}>
          {t("settingsRedoOnboarding")} <ArrowRight className="h-4 w-4" />
        </Link>
        <Link to="/" className={mcButton({ variant: "outline" })}>
          <LogOut className="h-4 w-4" />
          {t("settingsLogout")}
        </Link>
      </div>
    </div>
  );
}
