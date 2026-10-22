import { createFileRoute, Link } from "@tanstack/react-router";
import {
  AlertCircle,
  ArrowLeft,
  Bookmark,
  Lightbulb,
  Loader2,
  Sigma,
  Sparkles,
  Star,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { Eyebrow, mcButton, Reveal } from "@/components/mathcook/primitives";
import { getCook, type Cook, type Step } from "@/lib/mathcook/data";
import { MathView, RichMathText } from "@/components/ui/MathView";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/lib/i18n";

function cleanImportantNote(note: string): string {
  return note.replace(/^(ចំណាំសំខាន់|ចំណាំ|Important Note|Note)\s*[៖:]\s*/i, "").trim();
}

function cleanTeacherNote(note: string): string {
  return note.replace(/^(ការពន្យល់ពីលោកគ្រូ|ការពន្យល់|Teacher's Explanation|Explanation)\s*[៖:]\s*/i, "").trim();
}

export const Route = createFileRoute("/app/solve/$id")({
  loader: async ({ params }) => {
    const cook = await getCook(params.id);
    return cook ?? null;
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
  component: Solver,
});

function SolverHeader({ cook }: { cook: Cook }) {
  const { t } = useLanguage();
  return (
    <Reveal>
      <Link to="/app/my-cooks" className="inline-flex items-center gap-2 font-display font-bold text-muted-foreground hover:text-primary">
        <ArrowLeft className="h-4 w-4" />
        {t("backToCooks")}
      </Link>
      <div className="mt-6"><Eyebrow>{cook.topic} · {cook.skill}</Eyebrow></div>
      <h1 className="mt-4 text-4xl font-black md:text-6xl">{t("letsCookThis")}</h1>
      <div className="mt-6 rounded-[2rem] bg-primary-soft px-6 py-8 text-center md:py-10">
        <div className="font-display text-3xl font-black text-primary md:text-5xl">
          <MathView math={cook.problem} />
        </div>
      </div>
    </Reveal>
  );
}

function UnderstandingPanel({ cook }: { cook: Cook }) {
  const { t } = useLanguage();
  const rows = [
    [t("topic"), cook.topic],
    [t("skill"), cook.skill],
    [t("method"), cook.method],
    [t("confidence"), cook.confidence],
  ];
  return (
    <Reveal delay={100} className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-soft">
      <p className="flex items-center gap-2 font-display text-sm font-extrabold uppercase tracking-[0.14em] text-primary">
        <Sparkles className="h-4 w-4" />{t("mathCookUnderstood")}
      </p>
      <dl className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
        {rows.map(([k, v]) => (
          <div key={k}><dt className="text-sm text-muted-foreground">{k}</dt>
            <dd className={cn("font-display text-lg font-black", k === t("confidence") && "text-success")}>{v}</dd></div>
        ))}
      </dl>
    </Reveal>
  );
}

interface CalcBlock {
  text?: string;
  math?: string;
}

function buildCalculationBlocks(step: Step): CalcBlock[] {
  // 1. If step has explicit calc_steps from backend
  if (step.calc_steps && step.calc_steps.length > 0) {
    return step.calc_steps.filter((s) => s.text || s.math);
  }

  // 2. Filter details to get meaningful short explanations
  const rawDetails = (step.details || []).map((d) => d.trim()).filter(Boolean);
  const explains = rawDetails.filter((dt) => {
    // Suppress standalone numerator / denominator labels without explanation
    if (/^(ភាគយក|ភាគបែង|Numerator|Denominator)[៖:]\s*(\$[^$]+\$|[0-9a-zA-Z^_{}=+\-*/\s\\]+)$/i.test(dt)) return false;
    // Suppress isolated arithmetic like 2^3 - 8 = 0, 2 - 2 = 0
    if (/^(\$)?\d+(\^|\*\*|\^\{[0-9]+\})\d+\s*[-+*/]\s*\d+\s*=\s*(\d+\s*[-+*/]\s*\d+\s*=\s*)?\d+(\$)?$/.test(dt)) return false;
    if (/^(\$)?\d+\s*[-+*/]\s*\d+\s*=\s*\d+(\$)?$/.test(dt)) return false;
    return true;
  });

  // 3. Split step.math into individual progression lines
  if (!step.math) {
    return explains.map((text) => ({ text }));
  }

  // Normalize newlines in step.math
  let cleanMath = step.math.trim();
  cleanMath = cleanMath
    .replace(/\\newline\b/g, "\n")
    .replace(/\\n\b/g, "\n")
    .replace(/\\\\/g, "\n");

  const mathLines = cleanMath.split(/\r?\n+/).map((l) => l.trim()).filter(Boolean);

  if (mathLines.length <= 1) {
    if (explains.length > 0) {
      return [{ text: explains[0], math: mathLines[0] }, ...explains.slice(1).map((text) => ({ text }))];
    }
    return [{ math: mathLines[0] }];
  }

  // Multi-line math progression:
  // e.g. line 0 is the starting expression, subsequent lines (line 1, line 2, ...) start with =
  const blocks: CalcBlock[] = [];

  // Line 0 (starting expression)
  blocks.push({ math: mathLines[0] });

  // Subsequent lines (e.g. line 1, 2, ... starting with = or transition)
  const subsequentMath = mathLines.slice(1);

  if (explains.length === subsequentMath.length) {
    // 1-to-1 match: each transition line gets its explanation before it!
    subsequentMath.forEach((mathLine, idx) => {
      blocks.push({
        text: explains[idx],
        math: mathLine,
      });
    });
  } else if (explains.length === 1 && subsequentMath.length >= 1) {
    // 1 explanation for the main transition (e.g. សម្រួលកត្តាសូន្យ (x - 2) ចេញ)
    subsequentMath.forEach((mathLine, idx) => {
      blocks.push({
        text: idx === subsequentMath.length - 1 ? explains[0] : undefined,
        math: mathLine,
      });
    });
  } else {
    // Distribute explains before math lines
    subsequentMath.forEach((mathLine, idx) => {
      blocks.push({
        text: explains[idx] || undefined,
        math: mathLine,
      });
    });
    for (let i = subsequentMath.length; i < explains.length; i++) {
      blocks.push({ text: explains[i] });
    }
  }

  return blocks;
}

function SolutionStep({ step, n }: { step: Step; n: number }) {
  const { t } = useLanguage();
  const calculationBlocks = buildCalculationBlocks(step);
  const hasCalculation = calculationBlocks.length > 0;

  return (
    <Reveal delay={n * 120} className="card-lift rounded-3xl border border-border bg-card p-6 shadow-soft md:p-8 space-y-5">
      <div>
        <p className="font-display text-xs font-black tracking-[0.18em] text-primary">
          {t("stepPrefix")} {String(n + 1).padStart(2, "0")}
        </p>
        <h3 className="mt-1 text-2xl font-black">{step.title}</h3>
        {step.body && (
          <div className="mt-2 text-muted-foreground leading-relaxed">
            <RichMathText text={step.body} />
          </div>
        )}
      </div>

      {/* 1. ការពន្យល់ (Teacher Explanation) */}
      {step.teacher_note && (
        <div className="border-l-2 border-primary/70 pl-4 py-1 space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-primary">
            <Lightbulb className="h-3.5 w-3.5 shrink-0" />
            <span>{t("teacherExplanation")}</span>
          </div>
          <div className="text-sm leading-relaxed text-foreground/90 font-medium">
            <RichMathText text={cleanTeacherNote(step.teacher_note)} />
          </div>
        </div>
      )}

      {/* 2. វិធីគណនា (Calculation Details containing math at consistent container font size with short explanations before equal lines) */}
      {hasCalculation && (
        <div className="space-y-2 pt-1">
          <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground">
            <Bookmark className="h-3.5 w-3.5 text-primary" />
            <span>{t("calculationDetails")}</span>
          </div>
          <div className="space-y-2.5 pl-3 border-l-2 border-border/80">
            {calculationBlocks.map((block, idx) => (
              <div key={idx} className="space-y-1">
                {block.text && (
                  <div className="text-left text-xs md:text-sm font-semibold text-muted-foreground pt-1 pb-0.5">
                    <RichMathText text={block.text.endsWith("៖") || block.text.endsWith(":") ? block.text : `${block.text}៖`} />
                  </div>
                )}
                {block.math && (
                  <div className="py-1 text-base md:text-lg font-semibold text-foreground flex flex-col items-center justify-center text-center overflow-x-auto w-full">
                    <MathView math={block.math} displayMode={true} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. ចំណាំ (Important Note, if present) */}
      {step.important_note && (
        <div className="border-l-2 border-amber-500 pl-4 py-1 space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-600 dark:text-amber-400">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span>{t("importantNote")}</span>
          </div>
          <div className="text-sm leading-relaxed text-foreground/90 font-medium">
            <RichMathText text={cleanImportantNote(step.important_note)} />
          </div>
        </div>
      )}

      {step.rule_formula &&
        !step.rule_formula.includes("\\frac{0}{0}") &&
        !step.rule_formula.includes("0/0") &&
        !step.rule_formula.includes("\\infty") &&
        !(step.important_note && (
          step.important_note.includes(step.rule_formula.trim()) ||
          step.important_note.includes("A - B^2") ||
          step.important_note.includes("a^2 - b^2")
        )) && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground pt-1">
            <span className="font-bold text-primary">{t("appliedRule")}៖</span>
            <span className="font-semibold text-foreground">
              <RichMathText text={step.rule_formula} />
            </span>
          </div>
        )}
    </Reveal>
  );
}

function FinalAnswer({ answer, conclusion }: { answer: string; conclusion?: string }) {
  const { t } = useLanguage();
  return (
    <Reveal className="rounded-[2rem] bg-primary p-8 text-center text-primary-foreground shadow-float md:p-10 space-y-4">
      <Star className="mx-auto h-9 w-9 animate-floaty fill-t-sun text-t-sun" />
      <p className="font-display text-xs font-black tracking-[0.2em] opacity-80">{t("finalAnswer")}</p>
      <div className="font-display text-3xl font-black md:text-4xl">
        <MathView math={answer} />
      </div>
      {conclusion && (
        <div className="pt-2 border-t border-primary-foreground/20 text-sm md:text-base font-medium opacity-95">
          <RichMathText text={conclusion} />
        </div>
      )}
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

function Solver() {
  const { id } = Route.useParams();
  const loaderData = Route.useLoaderData();
  const [cook, setCook] = useState<Cook | null>(loaderData ?? null);
  const [loading, setLoading] = useState(!loaderData);
  const { t } = useLanguage();

  useEffect(() => {
    if (!cook) {
      getCook(id).then((c) => {
        if (c) {
          setCook(c);
        }
        setLoading(false);
      });
    }
  }, [id, cook]);

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="font-display text-sm font-bold text-muted-foreground">
            {t("loading") || "កំពុងផ្ទុកដំណោះស្រាយ..."}
          </p>
        </div>
      </div>
    );
  }

  if (!cook) {
    return (
      <div className="py-20 text-center">
        <h1 className="text-4xl font-black">{t("cookNotFound")}</h1>
        <Link to="/app/my-cooks" className={cn(mcButton(), "mt-6")}>
          {t("backToCooks")}
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
      <div>
        <SolverHeader cook={cook} />
        <UnderstandingPanel cook={cook} />
        {cook.teacher_header && (
          <div className="mt-8 flex items-center gap-2.5 border-b border-border/60 pb-3 text-primary">
            <Sparkles className="h-5 w-5 shrink-0" />
            <span className="font-bold text-lg font-display">
              {cook.teacher_header.replace(/ពីលោកគ្រូ|លោកគ្រូ/g, "").trim()}
            </span>
          </div>
        )}
        <div className="mt-6 space-y-5">{cook.steps.map((s, i) => <SolutionStep key={i} step={s} n={i} />)}</div>
        <div className="mt-8">
          <FinalAnswer answer={cook.answer} conclusion={cook.conclusion_km || cook.conclusion_en} />
        </div>
      </div>
      <aside className="space-y-6">
        <SideCard icon={<Lightbulb className="h-5 w-5" />} title={t("whyThisMethod")} tone="bg-primary-soft text-primary">
          <p className="whitespace-pre-line">{cook.why}</p>
        </SideCard>
        {cook.formula && (
          <SideCard icon={<Sigma className="h-5 w-5" />} title={t("formula")} tone="bg-t-sky/15 text-t-sky">
            <div className="py-2 font-display font-bold text-foreground">
              <MathView math={cook.formula} />
            </div>
          </SideCard>
        )}
        <SideCard icon={<TriangleAlert className="h-5 w-5" />} title={t("commonMistake")} tone="bg-t-coral/15 text-t-coral">
          <p className="whitespace-pre-line">{cook.mistake}</p>
        </SideCard>
      </aside>
    </div>
  );
}
