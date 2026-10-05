import { cva, type VariantProps } from "class-variance-authority";
import { useEffect, useRef, type ReactNode, type ElementType } from "react";
import { cn } from "@/lib/utils";

export const mcButton = cva(
  "inline-flex items-center justify-center gap-2 rounded-full font-display font-extrabold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "bg-primary text-primary-foreground shadow-soft hover:bg-primary-deep hover:-translate-y-0.5 hover:shadow-float",
        soft: "bg-primary-soft text-accent-foreground hover:bg-secondary hover:-translate-y-0.5",
        ghost: "text-foreground hover:bg-muted",
        outline: "bg-card text-foreground border border-border hover:border-primary hover:text-primary",
        inverse: "bg-card text-primary hover:-translate-y-0.5 hover:shadow-float",
      },
      size: {
        sm: "h-10 px-5 text-sm",
        md: "h-12 px-6 text-base",
        lg: "h-14 px-8 text-lg",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);
export type McButtonProps = VariantProps<typeof mcButton>;

export function Reveal({
  children,
  className,
  delay = 0,
  as: Tag = "div",
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
  as?: ElementType;
}) {
  const ref = useRef<HTMLElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e?.isIntersecting) {
          el.classList.add("is-visible");
          io.disconnect();
        }
      },
      { threshold: 0.15 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <Tag ref={ref} className={cn("reveal", className)} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </Tag>
  );
}

export function Eyebrow({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full bg-primary-soft px-4 py-1.5 font-display text-xs font-extrabold uppercase tracking-[0.16em] text-primary">
      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
      {children}
    </span>
  );
}

export function SectionTitle({ eyebrow, title, sub }: { eyebrow?: string; title: ReactNode; sub?: string }) {
  return (
    <Reveal className="mx-auto max-w-3xl text-center">
      {eyebrow && <Eyebrow>{eyebrow}</Eyebrow>}
      <h2 className="mt-5 text-4xl font-black leading-[1.05] md:text-6xl">{title}</h2>
      {sub && <p className="mt-5 text-lg text-muted-foreground">{sub}</p>}
    </Reveal>
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <svg viewBox="0 0 40 40" className="h-9 w-9" aria-hidden>
        <rect width="40" height="40" rx="12" className="fill-primary" />
        {/* chef hat */}
        <path
          d="M13 21c-2.6 0-4-2-4-4s1.8-4 4-3.6C13.6 10.6 16.4 9 20 9s6.4 1.6 7 4.4c2.2-.4 4 1.6 4 3.6s-1.4 4-4 4v3H13v-3Z"
          className="fill-primary-foreground"
        />
        {/* equation brackets base */}
        <path d="M13 27h14v2.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 13 29.5V27Z" className="fill-primary-foreground" />
        <path d="M18 17.5h4M20 15.5v4" strokeWidth="1.8" strokeLinecap="round" className="stroke-primary" />
      </svg>
      <span className="font-display text-xl font-black tracking-tight">
        Math<span className="text-primary">Cook</span>
      </span>
    </span>
  );
}
