import {
  Variable,
  Sigma,
  Triangle,
  Waves,
  Dices,
  ChartSpline,
  Equal,
  ChartColumn,
  type LucideIcon,
} from "lucide-react";

export type Topic = {
  name: string;
  desc: string;
  icon: LucideIcon;
  /** tailwind classes using design tokens */
  tone: string;
  glyph: string;
};

export const TOPICS: Topic[] = [
  { name: "Algebra", desc: "Expressions, factoring, and solving for x.", icon: Variable, tone: "bg-primary-soft text-primary", glyph: "x²" },
  { name: "Calculus", desc: "Limits, derivatives, and integrals, step by step.", icon: Sigma, tone: "bg-t-coral/15 text-t-coral", glyph: "∫" },
  { name: "Geometry", desc: "Shapes, angles, areas, and proofs.", icon: Triangle, tone: "bg-t-mint/15 text-t-mint", glyph: "△" },
  { name: "Trigonometry", desc: "Sine, cosine, identities, and unit circles.", icon: Waves, tone: "bg-t-sky/15 text-t-sky", glyph: "sin" },
  { name: "Functions", desc: "Domains, ranges, graphs, and transformations.", icon: ChartSpline, tone: "bg-t-rose/15 text-t-rose", glyph: "f(x)" },
  { name: "Probability", desc: "Chances, outcomes, and combinations.", icon: Dices, tone: "bg-t-sun/20 text-t-sun", glyph: "P" },
  { name: "Statistics", desc: "Mean, variance, and reading data clearly.", icon: ChartColumn, tone: "bg-t-sky/15 text-t-sky", glyph: "σ" },
  { name: "Equations", desc: "Linear, quadratic, and systems of equations.", icon: Equal, tone: "bg-t-mint/15 text-t-mint", glyph: "=" },
];
