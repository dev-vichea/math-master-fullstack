import { useNavigate, Link } from "@tanstack/react-router";
import { ArrowRight, Camera, Keyboard, CheckCircle2, Loader2, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { mcButton, Reveal } from "@/components/mathcook/primitives";
import { COOKS, submitProblem, extractMathFromImage } from "@/lib/mathcook/data";
import { CookCard, FloatingGlyphs } from "./shared";
import { cn } from "@/lib/utils";
import { MathLiveField, cleanMinimalMath, type MathLiveFieldRef } from "@/components/mathcook/MathLiveField";
import { MathView } from "@/components/ui/MathView";
import { toast } from "sonner";

export function ProblemUploader({
  onFile,
  imagePreview,
  fileName,
  instruction,
  scanning,
  onRemove,
}: {
  onFile: (f: File) => void;
  imagePreview?: string | null;
  fileName?: string | null;
  instruction?: string | null;
  scanning?: boolean;
  onRemove?: () => void;
}) {
  const [drag, setDrag] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) onFile(f);
    e.target.value = "";
  };

  if (imagePreview) {
    return (
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        className={cn(
          "card-lift relative flex flex-col justify-between rounded-[2rem] bg-card p-6 shadow-soft ring-1 ring-border/70 transition-all md:p-8",
          drag && "scale-[1.01] ring-2 ring-primary bg-primary-soft/30"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/png,image/jpeg,image/webp,application/pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Top bar with status and remove button */}
        <div className="flex items-center justify-between pb-2">
          <div className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-xl bg-primary-soft text-primary shadow-xs">
              <Camera className="h-4 w-4" />
            </span>
            <span className="truncate max-w-[200px] font-display text-sm font-bold text-foreground">
              {fileName || "Problem Image"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {scanning ? (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-3 py-1 font-display text-xs font-black text-primary animate-pulse">
                <Loader2 className="h-3.5 w-3.5 animate-spin" /> Scanning OCR...
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 font-display text-xs font-black text-emerald-600">
                <CheckCircle2 className="h-3.5 w-3.5" /> Math Extracted
              </span>
            )}

            {onRemove && (
              <button
                type="button"
                onClick={onRemove}
                className="grid h-8 w-8 place-items-center rounded-full text-muted-foreground transition hover:bg-destructive/10 hover:text-destructive"
                title="Remove image"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {/* Image Preview Container */}
        <div className="relative my-2 flex h-48 w-full items-center justify-center overflow-hidden rounded-2xl border border-border/70 bg-muted/40 p-2 shadow-inner">
          <img
            src={imagePreview}
            alt="Math Problem"
            className="max-h-full max-w-full rounded-xl object-contain shadow-sm"
          />

          {scanning && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-background/70 backdrop-blur-xs transition-all">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="font-display text-xs font-extrabold text-foreground">
                Analyzing mathematical symbols with LaTeX-OCR...
              </p>
            </div>
          )}
        </div>

        {instruction && (
          <div className="my-1.5 flex items-center gap-2 rounded-xl bg-primary/10 px-3 py-1.5 text-xs font-semibold text-primary">
            <span className="font-extrabold uppercase tracking-wider text-[10px] bg-primary text-primary-foreground px-1.5 py-0.5 rounded">
              Goal
            </span>
            <span className="truncate">{instruction}</span>
          </div>
        )}

        {/* Footer actions */}
        <div className="flex items-center justify-between pt-2">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="font-display text-xs font-bold text-primary transition hover:underline"
          >
            Change Image
          </button>
          <span className="font-display text-xs font-semibold text-muted-foreground">
            Confirm math below & click Cook It →
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={handleDrop}
      className={cn(
        "card-lift flex flex-col items-center rounded-[2rem] border-2 border-dashed bg-card p-8 text-center shadow-soft transition-all md:p-10",
        drag ? "scale-[1.02] border-primary bg-primary-soft" : "border-primary/30"
      )}
    >
      <span className="grid h-16 w-16 place-items-center rounded-3xl bg-primary text-primary-foreground shadow-soft">
        <Camera className="h-7 w-7" />
      </span>
      <h3 className="mt-5 text-2xl font-black">Upload a worksheet or problem</h3>
      <p className="mt-2 text-muted-foreground">
        {drag ? "Drop it right here!" : "Image, worksheet or PDF · drag & drop"}
      </p>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp,application/pdf"
        className="hidden"
        onChange={handleFileChange}
      />
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        className={cn(mcButton(), "mt-6")}
      >
        Upload Problem
      </button>
    </div>
  );
}

export function ProblemInput({
  value,
  onChange,
  onSubmit,
  mathFieldRef,
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: (v: string) => void;
  mathFieldRef?: React.RefObject<MathLiveFieldRef | null>;
}) {
  const fallbackRef = useRef<MathLiveFieldRef>(null);
  const activeRef = mathFieldRef || fallbackRef;

  return (
    <MathLiveField
      ref={activeRef}
      value={value}
      onChange={onChange}
      onSubmit={() => {
        if (value.trim()) onSubmit(value.trim());
      }}
      placeholder="Type an equation (e.g. y = 2x^2 + 1)"
    />
  );
}

const PHASES = ["Reading problem", "Understanding question", "Identifying topic", "Choosing method", "Cooking solution"];
const WS_PHASES = ["Reading worksheet", "Finding problems", "Understanding instructions", "Classifying topics", "Choosing methods", "Solving", "Explaining"];

export function CookingProgress({ onDone, worksheet }: { onDone: () => void; worksheet?: boolean }) {
  const PHASES_ = worksheet ? WS_PHASES : PHASES;
  const [i, setI] = useState(0);
  useEffect(() => {
    if (i >= PHASES_.length) { const t = setTimeout(onDone, 500); return () => clearTimeout(t); }
    const t = setTimeout(() => setI(i + 1), worksheet ? 650 : 900);
    return () => clearTimeout(t);
  }, [i, onDone]);
  return (
    <div className="mx-auto max-w-2xl rounded-[2rem] bg-card p-8 text-center shadow-float md:p-12">
      <div className="mx-auto grid h-20 w-20 animate-floaty place-items-center rounded-3xl bg-primary-soft font-display text-3xl font-black text-primary">∑</div>
      <h2 className="mt-6 text-3xl font-black md:text-4xl">{worksheet ? "Cooking your worksheet..." : "Cooking your problem..."}</h2>
      <ol className="mt-8 space-y-3 text-left">
        {PHASES_.map((p, n) => {
          const done = n < i, active = n === i;
          return (
            <li key={p} className={cn("flex items-center gap-4 rounded-2xl p-4 transition-all duration-500", active ? "bg-primary-soft" : done ? "bg-muted/60" : "opacity-50")}>
              <span className={cn("font-display text-sm font-black", active || done ? "text-primary" : "text-muted-foreground")}>{String(n + 1).padStart(2, "0")}</span>
              <span className="flex-1 font-display font-bold">{p}</span>
              {done ? <CheckCircle2 className="h-5 w-5 text-success" /> : active ? <Loader2 className="h-5 w-5 animate-spin text-primary" /> : null}
            </li>
          );
        })}
      </ol>
      <div className="mt-6 h-2 overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full bg-primary transition-[width] duration-700" style={{ width: `${(i / PHASES_.length) * 100}%` }} />
      </div>
    </div>
  );
}

export function RecentCooks() {
  const recent = COOKS.slice(0, 3);
  return (
    <section className="mt-20">
      <div className="mb-6 flex items-end justify-between">
        <h2 className="text-3xl font-black">Recent cooks</h2>
        <Link to="/app/my-cooks" className="font-display font-extrabold text-primary hover:underline">See all →</Link>
      </div>
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{recent.map((c) => <CookCard key={c.id} cook={c} />)}</div>
    </section>
  );
}

export function CookHome() {
  const navigate = useNavigate();
  const [cooking, setCooking] = useState<{ id: string; worksheet: boolean } | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [instruction, setInstruction] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [mathValue, setMathValue] = useState("");
  const mathFieldRef = useRef<MathLiveFieldRef>(null);

  const start = async (input: string | File) => {
    const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
    if (mvk?.visible) {
      mvk.hide({ animate: false });
    }
    try {
      const id = await submitProblem(input);
      setCooking({ id, worksheet: false });
    } catch (err: any) {
      toast.error(err.message || "Failed to solve problem");
    }
  };

  const handleFileDrop = async (file: File) => {
    const url = URL.createObjectURL(file);
    setImagePreview(url);
    setFileName(file.name);
    setScanning(true);

    try {
      toast.info("Extracting math formula with LaTeX-OCR...");
      const result = await extractMathFromImage(file);
      if (result.instruction) {
        setInstruction(result.instruction);
      }
      const rawMath = result.expression || result.detectedText || "";
      const mathExpr = cleanMinimalMath(rawMath);
      if (mathExpr) {
        setMathValue(mathExpr);
        mathFieldRef.current?.setValue(mathExpr);
        toast.success("Math formula extracted!");
        setTimeout(() => {
          mathFieldRef.current?.focus();
        }, 150);
      } else {
        toast.warning("Could not clearly read formula. You can edit it directly in the field.");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to scan image. You can type the formula directly.");
    } finally {
      setScanning(false);
    }
  };

  const handleRemoveImage = () => {
    if (imagePreview && imagePreview.startsWith("blob:")) {
      URL.revokeObjectURL(imagePreview);
    }
    setImagePreview(null);
    setFileName(null);
    setInstruction(null);
    setScanning(false);
  };

  const handleSampleImage = async (path: string) => {
    try {
      const res = await fetch(path);
      const blob = await res.blob();
      const file = new File([blob], path.split("/").pop() || "sample.png", { type: blob.type || "image/png" });
      await handleFileDrop(file);
    } catch (err: any) {
      toast.error("Failed to load sample image");
    }
  };

  if (cooking) {
    return (
      <div className="py-6">
        <CookingProgress
          worksheet={cooking.worksheet}
          onDone={() =>
            cooking.worksheet
              ? navigate({ to: "/app/solve/worksheet" })
              : navigate({ to: "/app/solve/$id", params: { id: cooking.id } })
          }
        />
      </div>
    );
  }

  return (
    <div className="relative">
      <FloatingGlyphs />
      <Reveal className="text-center">
        <div className="flex flex-wrap justify-center gap-2">
          {["Understand", "Classify", "Solve", "Explain"].map((s, n) => (
            <span
              key={s}
              className="inline-flex items-center gap-2 font-display text-xs font-extrabold uppercase tracking-[0.14em] text-primary"
            >
              <span className="rounded-full bg-primary-soft px-3 py-1">{s}</span>
              {n < 3 && "→"}
            </span>
          ))}
        </div>
        <h1 className="mx-auto mt-5 max-w-3xl text-5xl font-black leading-[1.02] md:text-7xl">
          What are we <span className="text-primary">cooking</span> today?
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-muted-foreground">
          Give me a math problem and I'll break it down step by step with LaTeX-OCR.
        </p>
      </Reveal>

      <Reveal delay={120} className="mx-auto mt-12 max-w-3xl">
        <ProblemUploader
          onFile={handleFileDrop}
          imagePreview={imagePreview}
          fileName={fileName}
          instruction={instruction}
          scanning={scanning}
          onRemove={handleRemoveImage}
        />
      </Reveal>

      <Reveal delay={200} className="mx-auto mt-10 max-w-3xl">
        <p className="mb-4 text-center font-display font-bold text-muted-foreground">
          or try these real exercises from your training set:
        </p>
        <div className="mb-5 flex flex-wrap justify-center gap-2">
          {[
            { label: "∫₂⁴ 4x dx", query: "\\int_{2}^{4} 4x dx" },
            { label: "y' = 2x² - x + 1", query: "y' = 2x^2 - x + 1" },
            { label: "y'' - 3y' + 2y = 0, y(0)=1, y'(0)=3", query: "y'' - 3y' + 2y = 0, y(0) = 1, y'(0) = 3" },
            { label: "y'/y = cos x, y(π/2) = e", query: "y'/y = cos x, y(pi/2) = e" },
          ].map((item) => (
            <button
              key={item.label}
              onClick={() => {
                setMathValue(item.query);
                mathFieldRef.current?.setValue(item.query);
                mathFieldRef.current?.focus();
              }}
              className="rounded-full bg-card px-4 py-2 font-display text-sm font-bold shadow-soft transition hover:scale-105 hover:bg-primary-soft hover:text-primary"
            >
              <MathView math={item.label} />
            </button>
          ))}
          <button
            onClick={() => handleSampleImage("/samples/differential_ex7.png")}
            className="flex items-center gap-1.5 rounded-full bg-primary/10 px-4 py-2 font-display text-sm font-black text-primary shadow-soft transition hover:scale-105 hover:bg-primary hover:text-primary-foreground"
          >
            <Camera className="h-4 w-4" /> Scan Photo: ឃ. y''-3y'+2y=0
          </button>
        </div>

        <ProblemInput
          value={mathValue}
          onChange={setMathValue}
          onSubmit={(confirmed) => start(confirmed)}
          mathFieldRef={mathFieldRef}
        />
      </Reveal>

      <RecentCooks />
    </div>
  );
}
