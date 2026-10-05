import { ArrowRight, PlayCircle } from "lucide-react";
import { Eyebrow, Logo, mcButton } from "./primitives";
import { TOPICS } from "./topics";
import { cn } from "@/lib/utils";

const SYMBOLS = [
  { s: "x²", c: "left-[6%] top-[12%]", d: "0s" },
  { s: "π", c: "right-[8%] top-[6%]", d: "1.2s" },
  { s: "∫", c: "left-[2%] bottom-[22%]", d: "2s" },
  { s: "√", c: "right-[2%] bottom-[30%]", d: "0.6s" },
  { s: "Δ", c: "left-[42%] top-[0%]", d: "2.6s" },
  { s: "Σ", c: "right-[30%] bottom-[2%]", d: "1.6s" },
  { s: "=", c: "left-[24%] bottom-[4%]", d: "3s" },
];

// positions on an ellipse around the center (percent)
const POS = [
  [50, 6], [85, 18], [90, 50], [85, 82], [50, 94], [15, 82], [10, 50], [15, 18],
];

export function TopicOrbit() {
  return (
    <div className="relative mx-auto aspect-square w-full max-w-[560px]">
      {SYMBOLS.map((x) => (
        <span key={x.s} className={cn("animate-drift absolute font-display text-2xl font-black text-primary/25 md:text-3xl", x.c)} style={{ animationDelay: x.d }}>
          {x.s}
        </span>
      ))}
      <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" aria-hidden>
        <circle cx="50" cy="50" r="30" fill="none" strokeWidth="0.25" strokeDasharray="1 1.5" className="stroke-primary/40" />
        <circle cx="50" cy="50" r="44" fill="none" strokeWidth="0.2" className="stroke-primary/15" />
        {POS.map(([x, y], i) =>
          i % 2 === 0 ? <line key={i} x1="50" y1="50" x2={x} y2={y} strokeWidth="0.2" className="stroke-primary/30" /> : null,
        )}
      </svg>
      {/* center */}
      <div className="absolute left-1/2 top-1/2 flex h-32 w-32 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-[2rem] bg-card shadow-float md:h-40 md:w-40">
        <div className="absolute inset-3 rounded-[1.5rem] bg-primary-soft" />
        <div className="relative scale-[1.6] md:scale-[2]">
          <Logo className="[&>span]:hidden" />
        </div>
      </div>
      {TOPICS.map((t, i) => {
        const [x, y] = POS[i] ?? [50, 50];
        const Icon = t.icon;
        return (
          <div key={t.name} className="absolute -translate-x-1/2 -translate-y-1/2" style={{ left: `${x}%`, top: `${y}%` }}>
            <div
              className="animate-floaty flex items-center gap-2 rounded-2xl bg-card px-2.5 py-2 shadow-soft transition-transform hover:scale-105 md:px-3"
              style={{ animationDelay: `${i * 0.7}s` }}
            >
              <span className={cn("flex h-8 w-8 items-center justify-center rounded-xl", t.tone)}>
                <Icon className="h-4 w-4" />
              </span>
              <span className="hidden pr-1 font-display text-sm font-extrabold sm:inline">{t.name}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function HeroSection() {
  return (
    <section id="top" className="px-3 pt-4 md:px-6">
      <div className="relative mx-auto max-w-7xl overflow-hidden rounded-[2.5rem] bg-secondary px-6 py-14 md:px-14 md:py-20">
        <div className="grid items-center gap-12 lg:grid-cols-[1.05fr_1fr]">
          <div>
            <Eyebrow>AI Math Companion</Eyebrow>
            <h1 className="mt-6 text-5xl font-black leading-[0.98] sm:text-6xl lg:text-7xl">
              Math doesn't have to be hard.{" "}
              <span className="relative whitespace-nowrap text-primary">
                Let's cook it.
                <svg viewBox="0 0 200 12" className="absolute -bottom-2 left-0 w-full" aria-hidden>
                  <path d="M2 8c50-6 140-8 196-2" fill="none" strokeWidth="4" strokeLinecap="round" className="stroke-primary/30" />
                </svg>
              </span>
            </h1>
            <p className="mt-7 max-w-xl text-lg leading-relaxed text-muted-foreground md:text-xl">
              Snap a worksheet, type a problem, or paste an equation. MathCook figures out what you're solving and walks you through every step.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <a href="#solve" className={mcButton({ size: "lg" })}>
                Start Cooking <ArrowRight className="h-5 w-5" />
              </a>
              <a href="#how" className={mcButton({ variant: "outline", size: "lg" })}>
                <PlayCircle className="h-5 w-5" /> See How It Works
              </a>
            </div>
            <div className="mt-10 flex items-center gap-6 text-sm text-muted-foreground">
              <div><span className="block font-display text-2xl font-black text-foreground">8</span>core topics</div>
              <div className="h-10 w-px bg-border" />
              <div><span className="block font-display text-2xl font-black text-foreground">Every</span>step explained</div>
              <div className="h-10 w-px bg-border" />
              <div><span className="block font-display text-2xl font-black text-foreground">Photo</span>or typed input</div>
            </div>
          </div>
          <TopicOrbit />
        </div>
      </div>
    </section>
  );
}
