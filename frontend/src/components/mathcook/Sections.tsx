import { ArrowRight, ArrowUpRight, Check, Eye, Brain, ChefHat, Sparkles, Github, Instagram, Twitter, Youtube } from "lucide-react";
import { Logo, mcButton, Reveal, SectionTitle, Eyebrow } from "./primitives";
import { TOPICS } from "./topics";
import { cn } from "@/lib/utils";
import pain1 from "@/assets/pain-1.jpg";
import pain2 from "@/assets/pain-2.jpg";
import pain3 from "@/assets/pain-3.jpg";

export function HowItWorks() {
  const steps = [
    { n: "01", t: "See it", d: "Upload or type your math problem.", icon: Eye },
    { n: "02", t: "Understand it", d: "MathCook identifies the topic and figures out what the question is asking.", icon: Brain },
    { n: "03", t: "Cook it", d: "Get a clear step-by-step solution with formulas and explanations.", icon: ChefHat },
  ];
  return (
    <section id="how" className="scroll-mt-24 px-3 md:px-6">
      <div className="mx-auto max-w-7xl rounded-[2.5rem] bg-secondary px-6 py-20 md:px-14 md:py-28">
        <SectionTitle eyebrow="How it works" title={<>From messy problem<br className="hidden md:block" /> to clean solution.</>} />
        <div className="relative mt-16 grid gap-10 md:grid-cols-3 md:gap-6">
          <div className="absolute left-[16%] right-[16%] top-10 hidden border-t-2 border-dashed border-primary/25 md:block" />
          {steps.map((s, i) => (
            <Reveal key={s.n} delay={i * 120} className="relative text-center">
              <div className="relative mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-primary font-display text-2xl font-black text-primary-foreground shadow-float ring-8 ring-secondary">
                {s.n}
              </div>
              <s.icon className="mx-auto mt-6 h-6 w-6 text-primary" />
              <h3 className="mt-3 text-2xl font-black">{s.t}</h3>
              <p className="mx-auto mt-2 max-w-xs text-muted-foreground">{s.d}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

export function ProblemUnderstanding() {
  const rows = [
    ["Topic", "Algebra"],
    ["Skill", "Factorization"],
    ["Method", "Quadratic Factorization"],
  ];
  return (
    <section id="learn" className="mx-auto max-w-7xl scroll-mt-24 px-5 py-24 md:py-32">
      <div className="grid items-center gap-14 lg:grid-cols-[0.9fr_1.1fr]">
        <Reveal>
          <Eyebrow>Smart understanding</Eyebrow>
          <h2 className="mt-5 text-4xl font-black leading-[1.05] md:text-6xl">
            It doesn't just solve. <span className="text-primary">It understands.</span>
          </h2>
          <p className="mt-6 max-w-md text-lg text-muted-foreground">
            Before a single number moves, MathCook reads the problem like a tutor would — what topic, which skill, and the best method to teach it.
          </p>
        </Reveal>
        <div className="grid items-center gap-4 sm:grid-cols-[1fr_auto_1fr_auto_1fr] lg:gap-3">
          <Reveal className="rounded-3xl bg-card p-6 shadow-soft">
            <p className="font-display text-xs font-extrabold uppercase tracking-widest text-muted-foreground">Problem</p>
            <p className="mt-3 font-display text-lg font-black">Factorize</p>
            <p className="mt-1 font-display text-2xl font-black text-primary">x² − 5x + 6</p>
          </Reveal>
          <ArrowRight className="mx-auto h-6 w-6 rotate-90 text-primary/50 sm:rotate-0" />
          <Reveal delay={120} className="rounded-3xl bg-primary p-6 text-primary-foreground shadow-float">
            <p className="flex items-center gap-1.5 font-display text-xs font-extrabold uppercase tracking-widest opacity-80"><Sparkles className="h-3.5 w-3.5" /> Classified</p>
            <dl className="mt-3 space-y-2.5">
              {rows.map(([k, v]) => (
                <div key={k}>
                  <dt className="text-xs opacity-70">{k}</dt>
                  <dd className="font-display font-extrabold leading-tight">{v}</dd>
                </div>
              ))}
              <div>
                <dt className="text-xs opacity-70">Confidence</dt>
                <dd className="mt-1 flex items-center gap-2 font-display font-extrabold">
                  <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-primary-foreground/25"><span className="block h-full w-[94%] rounded-full bg-primary-foreground" /></span>
                  High
                </dd>
              </div>
            </dl>
          </Reveal>
          <ArrowRight className="mx-auto h-6 w-6 rotate-90 text-primary/50 sm:rotate-0" />
          <Reveal delay={240} className="rounded-3xl bg-card p-6 shadow-soft ring-2 ring-success/30">
            <p className="font-display text-xs font-extrabold uppercase tracking-widest text-success">→ Solution</p>
            <p className="mt-3 font-display text-2xl font-black">(x − 2)(x − 3)</p>
            <p className="mt-2 text-sm text-muted-foreground">Verified by expanding back.</p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

export function SolutionPreview() {
  const steps = [
    { t: "Find two numbers whose product is 6 and sum is −5.", why: "Factoring x² + bx + c means finding p·q = c and p + q = b." },
    { t: "The numbers are −2 and −3.", math: "(−2)(−3) = 6   ·   −2 + (−3) = −5" },
    { t: "Rewrite the equation.", math: "(x − 2)(x − 3) = 0" },
    { t: "Solve each factor.", math: "x = 2   or   x = 3", why: "Zero product rule: if a·b = 0, then a = 0 or b = 0." },
  ];
  return (
    <section className="mx-auto max-w-7xl px-5 pb-24 md:pb-32">
      <SectionTitle eyebrow="Step-by-step" title={<>Don't just get the answer.<br className="hidden md:block" /> <span className="text-primary">Understand</span> the answer.</>} />
      <Reveal className="mx-auto mt-14 max-w-4xl overflow-hidden rounded-[2rem] bg-card shadow-float">
        <div className="flex items-center justify-between border-b border-border px-6 py-4 md:px-8">
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full bg-t-coral/60" /><span className="h-3 w-3 rounded-full bg-t-sun/70" /><span className="h-3 w-3 rounded-full bg-t-mint/60" />
          </div>
          <span className="rounded-full bg-primary-soft px-3 py-1 font-display text-xs font-extrabold text-primary">Algebra · Quadratics</span>
        </div>
        <div className="p-6 md:p-10">
          <p className="font-display text-xs font-extrabold uppercase tracking-widest text-muted-foreground">Problem</p>
          <p className="mt-2 font-display text-3xl font-black md:text-4xl">x² − 5x + 6 = 0</p>
          <ol className="mt-8 space-y-4">
            {steps.map((s, i) => (
              <li key={i} className="group flex gap-4 rounded-3xl bg-muted/60 p-5 transition-colors hover:bg-primary-soft md:gap-6 md:p-6">
                <span className="font-display text-sm font-black text-primary">Step<br /><span className="text-2xl">0{i + 1}</span></span>
                <div className="flex-1">
                  <p className="font-display text-lg font-extrabold">{s.t}</p>
                  {s.math && <p className="mt-2 inline-block rounded-xl bg-card px-4 py-2 font-display text-lg font-black text-primary shadow-soft">{s.math}</p>}
                  {s.why && <p className="mt-2 text-sm text-muted-foreground"><span className="font-bold text-foreground">Why? </span>{s.why}</p>}
                </div>
              </li>
            ))}
          </ol>
          <div className="mt-8 flex flex-wrap items-center justify-between gap-4">
            <span className="inline-flex items-center gap-2 rounded-full bg-success/15 px-4 py-2 font-display font-extrabold text-success">
              <Check className="h-4 w-4" /> Answer understood
            </span>
            <span className="text-sm text-muted-foreground">Try a similar problem →</span>
          </div>
        </div>
      </Reveal>
    </section>
  );
}

export function TopicGrid() {
  return (
    <section id="topics" className="mx-auto max-w-7xl scroll-mt-24 px-5 pb-24 md:pb-32">
      <SectionTitle eyebrow="Topics" title="Pick your battlefield." sub="From your first equation to your final exam." />
      <div className="mt-14 grid grid-cols-2 gap-4 md:gap-6 lg:grid-cols-4">
        {TOPICS.map((t, i) => (
          <Reveal key={t.name} delay={(i % 4) * 80}>
            <a href="#solve" className="card-lift group relative flex h-full flex-col overflow-hidden rounded-[1.75rem] bg-card p-5 shadow-soft md:p-7">
              <span className="pointer-events-none absolute -right-2 -top-4 font-display text-7xl font-black text-foreground/[0.04] transition-transform group-hover:scale-110">{t.glyph}</span>
              <span className={cn("flex h-14 w-14 items-center justify-center rounded-2xl md:h-16 md:w-16", t.tone)}>
                <t.icon className="h-7 w-7 md:h-8 md:w-8" />
              </span>
              <h3 className="mt-6 text-xl font-black md:text-2xl">{t.name}</h3>
              <p className="mt-1.5 flex-1 text-sm text-muted-foreground">{t.desc}</p>
              <ArrowUpRight className="mt-5 h-5 w-5 text-muted-foreground transition-all group-hover:translate-x-1 group-hover:-translate-y-1 group-hover:text-primary" />
            </a>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

export function PainPointCards() {
  const cards = [
    { q: "What is this question even asking?", img: pain1 },
    { q: "Why did they suddenly use THAT formula?", img: pain2 },
    { q: "I got the answer... but I don't understand it.", img: pain3 },
  ];
  return (
    <section className="mx-auto max-w-7xl px-5 pb-24 md:pb-32">
      <SectionTitle title="We've all been there." />
      <div className="mt-14 grid gap-6 md:grid-cols-3">
        {cards.map((c, i) => (
          <Reveal key={c.q} delay={i * 120}>
            <figure className="card-lift h-full overflow-hidden rounded-[2rem] bg-card shadow-soft">
              <img src={c.img} alt="" loading="lazy" width={944} height={704} className="aspect-[4/3] w-full object-cover" />
              <figcaption className="p-6 font-display text-xl font-black leading-snug md:text-2xl">“{c.q}”</figcaption>
            </figure>
          </Reveal>
        ))}
      </div>
      <Reveal className="mt-16 text-center">
        <p className="font-display text-3xl font-black md:text-5xl">That's exactly why <span className="text-primary">MathCook</span> exists.</p>
      </Reveal>
    </section>
  );
}

export function FinalCTA() {
  const syms = [
    ["x²", "left-[6%] top-[18%]"], ["π", "right-[10%] top-[14%]"], ["∫", "left-[14%] bottom-[14%]"],
    ["√", "right-[6%] bottom-[22%]"], ["Σ", "left-[44%] top-[6%]"], ["Δ", "right-[30%] bottom-[8%]"],
  ];
  return (
    <section className="px-3 pb-10 md:px-6">
      <div className="relative mx-auto max-w-7xl overflow-hidden rounded-[2.5rem] bg-primary px-6 py-20 text-center text-primary-foreground md:py-28">
        {syms.map(([s, c], i) => (
          <span key={s} className={cn("animate-drift absolute font-display text-4xl font-black opacity-20 md:text-6xl", c)} style={{ animationDelay: `${i * 0.8}s` }}>{s}</span>
        ))}
        <Reveal className="relative">
          <h2 className="text-4xl font-black md:text-7xl">Ready to cook some math?</h2>
          <p className="mx-auto mt-5 max-w-xl text-lg opacity-85 md:text-xl">Bring your hardest problem. We'll take it one step at a time.</p>
          <a href="#solve" className={cn(mcButton({ variant: "inverse", size: "lg" }), "mt-10 w-full sm:w-auto")}>
            Start Cooking <ArrowRight className="h-5 w-5" />
          </a>
        </Reveal>
      </div>
    </section>
  );
}

export function Footer() {
  const links = ["Solve", "Learn", "Topics", "About", "Contact"];
  return (
    <footer className="mx-auto max-w-7xl px-5 py-12">
      <div className="flex flex-col gap-8 md:flex-row md:items-center md:justify-between">
        <div>
          <Logo />
          <p className="mt-3 max-w-xs text-muted-foreground">Making math easier to understand, one problem at a time.</p>
        </div>
        <nav className="flex flex-wrap gap-x-6 gap-y-2">
          {links.map((l) => (
            <a key={l} href={`#${l.toLowerCase()}`} className="font-display font-bold text-muted-foreground hover:text-primary">{l}</a>
          ))}
        </nav>
        <div className="flex gap-2">
          {[Twitter, Instagram, Youtube, Github].map((I, i) => (
            <a key={i} href="#" aria-label="Social link" className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary text-primary transition hover:-translate-y-0.5 hover:bg-primary hover:text-primary-foreground">
              <I className="h-4 w-4" />
            </a>
          ))}
        </div>
      </div>
      <p className="mt-10 border-t border-border pt-6 text-sm text-muted-foreground">© 2026 MathCook. All rights reserved.</p>
    </footer>
  );
}
