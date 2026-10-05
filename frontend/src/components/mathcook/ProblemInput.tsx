import { useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Camera, Keyboard, Upload, ArrowRight, Check, Loader2 } from "lucide-react";
import { mcButton, Reveal, SectionTitle } from "./primitives";
import { submitProblem } from "@/lib/mathcook/data";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function ProblemInput() {
  const navigate = useNavigate();
  const [drag, setDrag] = useState(false);
  const [fileObj, setFileObj] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [typing, setTyping] = useState(false);
  const [problem, setProblem] = useState("");
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (f: File) => {
    setFileObj(f);
    setFileName(f.name);
  };

  const handleCookFile = async () => {
    if (!fileObj || loading) return;
    setLoading(true);
    try {
      const id = await submitProblem(fileObj);
      navigate({ to: "/app/solve/$id", params: { id } });
    } catch (err: any) {
      toast.error(err.message || "Failed to scan and solve problem");
    } finally {
      setLoading(false);
    }
  };

  const handleCookText = async (textToCook?: string) => {
    const target = textToCook || problem;
    if (!target.trim() || loading) return;
    setLoading(true);
    try {
      const id = await submitProblem(target);
      navigate({ to: "/app/solve/$id", params: { id } });
    } catch (err: any) {
      toast.error(err.message || "Failed to solve problem");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="solve" className="mx-auto max-w-7xl scroll-mt-24 px-5 py-24 md:py-32">
      <SectionTitle eyebrow="Start here" title="What are we cooking today?" sub="Two ways in. Pick whichever is faster for you." />
      <div className="mt-14 grid gap-6 md:grid-cols-2">
        <Reveal>
          <div
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDrag(false);
              const f = e.dataTransfer.files[0];
              if (f) handleFileSelect(f);
            }}
            className={cn(
              "card-lift group relative flex h-full flex-col rounded-[2rem] border-2 border-dashed bg-card p-8 shadow-soft md:p-10",
              drag ? "border-primary bg-primary-soft" : "border-border",
            )}
          >
            <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-soft text-primary transition-transform group-hover:-rotate-6">
              <Camera className="h-8 w-8" />
            </span>
            <h3 className="mt-6 text-3xl font-black">Upload a Problem</h3>
            <p className="mt-2 text-muted-foreground">Drop a worksheet or math problem here (LaTeX-OCR)</p>
            <div className="mt-8 flex flex-1 items-center justify-center rounded-3xl bg-muted/70 py-10 text-center">
              {fileName ? (
                <div className="space-y-2">
                  <p className="flex items-center justify-center gap-2 font-display font-bold text-success">
                    <Check className="h-5 w-5" /> {fileName} ready to cook
                  </p>
                  <button
                    onClick={handleCookFile}
                    disabled={loading}
                    className={cn(mcButton({ variant: "primary" }), "mt-3")}
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />} Cook Image Now
                  </button>
                </div>
              ) : (
                <p className="font-display font-bold text-muted-foreground">
                  <Upload className="mx-auto mb-2 h-6 w-6" />Drag & drop · PNG, JPG, PDF
                </p>
              )}
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="image/*,.pdf"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFileSelect(f);
              }}
            />
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={() => inputRef.current?.click()}
                className={cn(mcButton({ variant: "outline" }))}
              >
                <Upload className="h-4 w-4" /> {fileName ? "Change Image" : "Upload Image"}
              </button>
              {fileName && (
                <button
                  onClick={handleCookFile}
                  disabled={loading}
                  className={cn(mcButton({ variant: "primary" }))}
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />} Cook Now
                </button>
              )}
            </div>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <div className="card-lift group flex h-full flex-col rounded-[2rem] border-2 border-transparent bg-card p-8 shadow-soft md:p-10">
            <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-t-coral/15 text-t-coral transition-transform group-hover:rotate-6">
              <Keyboard className="h-8 w-8" />
            </span>
            <h3 className="mt-6 text-3xl font-black">Type a Problem</h3>
            <p className="mt-2 text-muted-foreground">Enter an equation or question manually</p>
            <div className="mt-8 flex flex-1 flex-col rounded-3xl bg-muted/70 p-5">
              {typing ? (
                <textarea
                  autoFocus
                  value={problem}
                  onChange={(e) => setProblem(e.target.value)}
                  placeholder="e.g. Solve x² − 5x + 6 = 0 or y' = 2x^2 - x + 1"
                  className="min-h-32 flex-1 resize-none bg-transparent font-display text-xl font-bold outline-none placeholder:text-muted-foreground/60"
                />
              ) : (
                <div className="flex flex-1 flex-wrap content-center justify-center gap-2">
                  {[
                    { label: "x² − 5x + 6 = 0", expr: "x^2 - 5x + 6 = 0" },
                    { label: "∫₂⁴ 4x dx", expr: "\\int_{2}^{4} 4x dx" },
                    { label: "y' = 2x² - x + 1", expr: "y' = 2x^2 - x + 1" },
                    { label: "y'' - 3y' + 2y = 0", expr: "y'' - 3y' + 2y = 0, y(0) = 1, y'(0) = 3" },
                  ].map((s) => (
                    <button
                      key={s.label}
                      onClick={() => {
                        setTyping(true);
                        setProblem(s.expr);
                      }}
                      className="rounded-full bg-card px-4 py-2 font-display font-bold shadow-soft transition hover:text-primary"
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            <button
              onClick={() => {
                if (typing) {
                  handleCookText();
                } else {
                  setTyping(true);
                }
              }}
              disabled={loading}
              className={cn(mcButton({ variant: typing ? "primary" : "soft" }), "mt-6 w-full sm:w-auto sm:self-start")}
            >
              {loading ? (
                <>Cooking... <Loader2 className="h-4 w-4 animate-spin" /></>
              ) : typing ? (
                <>Cook it <ArrowRight className="h-4 w-4" /></>
              ) : (
                "Start Typing"
              )}
            </button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
