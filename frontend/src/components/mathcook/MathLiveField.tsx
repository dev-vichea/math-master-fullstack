import React, { useEffect, useRef, useState, useImperativeHandle, forwardRef } from "react";
import { Keyboard, ArrowRight, Trash2 } from "lucide-react";
import { MathView } from "@/components/ui/MathView";
import { mcButton } from "./primitives";
import { cn } from "@/lib/utils";

declare global {
  namespace JSX {
    interface IntrinsicElements {
      "math-field": any;
    }
  }
  namespace React.JSX {
    interface IntrinsicElements {
      "math-field": any;
    }
  }
}

/**
 * Strips all Khmer characters, non-math instructions, and labels,
 * ensuring the math field receives strictly minimal math only.
 */
export function cleanMinimalMath(input: string): string {
  if (!input || !input.trim()) return "";

  let s = input.trim();

  // 1. Unwrap outer \begin{aligned} ... \end{aligned} or \begin{gathered}
  s = s.replace(/^\s*\\begin\{(?:aligned|gathered)\}\s*(?:&|\s)*/, "");
  s = s.replace(/\s*\\end\{(?:aligned|gathered)\}\s*$/, "");
  s = s.replace(/^&+\s*/, "");

  // 2. Strip any \text{...}, \mathrm{...} containing Khmer or non-math words
  s = s.replace(/\\(?:text|mathrm|mathbf|textbf|textit)\{[^{}]*[\u1780-\u17FF\u19E0-\u19FF][^{}]*\}/g, " ");
  s = s.replace(/\\(?:text|mathrm|mathbf|textbf|textit)\{\s*\}/g, " ");

  // 3. Strip all Khmer characters and Khmer punctuation
  s = s.replace(/[\u1780-\u17FF\u19E0-\u19FF\u17D4-\u17DA]/g, " ");

  // 4. Clean LaTeX spacing tokens like \; \, \! \: \quad \qquad
  s = s.replace(/\\+([;,!:])+/g, " ");
  s = s.replace(/\\(?:quad|qquad|hfill|vfill|thickspace|medspace|thinspace)\b/g, " ");

  // 5. Strip leading exercise headers/labels (e.g. 1., (a), a., ឃ., ឌ,)
  s = s.replace(
    /^\s*(?:\([a-zA-Z0-9]{1,2}\)[\.៖:,]?|[a-zA-Z0-9]{1,2}[\)\.៖:,](?!\d))\s*/g,
    ""
  );
  s = s.replace(/^\s*(?:[\\/](?:tilde|bar|hat|mathcal|mathbf|mathrm|text)\{[^{}]*\}[\)\.៖:,]?)\s*/g, "");

  // 6. Clean repeated OCR dashes (e.g. - - - or ---)
  s = s.replace(/(?:-\s*){2,}/g, " ");

  // 7. Clean leading alignment tokens or newlines left from empty text lines
  s = s.replace(/^(?:\\\\|&|\s)+/, "");

  // 8. Clean solitary leading punctuation like , = or : = or .
  s = s.replace(/^[\s,;:.]+/, "");
  if (s.startsWith("=") && !/^[a-zA-Z]\s*=/.test(s)) {
    s = s.replace(/^=\s*/, "");
  }
  s = s.replace(/^[\s,;:.]+/, "");

  // 9. Clean trailing OCR noise (stray dots, commas, solitary 'i' at end)
  s = s.replace(/[\s,;:.|~]+$/, "");
  s = s.replace(/(?<=\d|\)|\]|\})\s+i\s*$/, "");

  return s.replace(/\s+/g, " ").trim();
}

export const formatTextAndMathForMathLive = cleanMinimalMath;


// Quick math symbol templates using MathLive's smart insertion tokens (#@ = selection, #? = placeholder)
export const MATH_SYMBOLS = [
  { label: "\\frac{a}{b}", latex: "\\frac{#@}{#?}", desc: "Fraction" },
  { label: "\\sqrt{x}", latex: "\\sqrt{#@}", desc: "Square root" },
  { label: "x^2", latex: "^{2}", desc: "Square" },
  { label: "x^n", latex: "^{#?}", desc: "Power / Exponent" },
  { label: "\\int", latex: "\\int #@ \\, dx", desc: "Indefinite Integral" },
  { label: "\\int_a^b", latex: "\\int_{#?}^{#?} #@ \\, dx", desc: "Definite Integral" },
  { label: "y'", latex: "y'", desc: "First derivative" },
  { label: "y''", latex: "y''", desc: "Second derivative" },
  { label: "\\frac{dy}{dx}", latex: "\\frac{dy}{dx}", desc: "Leibniz derivative" },
  { label: "\\lim", latex: "\\lim_{x \\to 0} #@", desc: "Limit as x approaches 0" },
  { label: "\\lim_{\\infty}", latex: "\\lim_{x \\to +\\infty} #@", desc: "Limit as x approaches infinity" },
  { label: "e^x", latex: "e^{#?}", desc: "Exponential" },
  { label: "\\ln(x)", latex: "\\ln(#@)", desc: "Natural log" },
  { label: "\\sin", latex: "\\sin(#@)", desc: "Sine" },
  { label: "\\cos", latex: "\\cos(#@)", desc: "Cosine" },
  { label: "\\tan", latex: "\\tan(#@)", desc: "Tangent" },
  { label: "\\pi", latex: "\\pi", desc: "Pi" },
  { label: "\\pm", latex: "\\pm", desc: "Plus-minus" },
  { label: "\\neq", latex: "\\neq", desc: "Not equal" },
  { label: "\\le", latex: "\\le", desc: "Less or equal" },
  { label: "\\ge", latex: "\\ge", desc: "Greater or equal" },
];

export interface MathLiveFieldRef {
  focus: () => void;
  setValue: (val: string) => void;
  insert: (latex: string) => void;
  getValue: () => string;
  showKeyboard: () => void;
  toggleKeyboard: () => void;
}

export interface MathLiveFieldProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit?: () => void;
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

export const MathLiveField = forwardRef<MathLiveFieldRef, MathLiveFieldProps>(
  function MathLiveField(
    {
      value,
      onChange,
      onSubmit,
      placeholder = "Type your equation or problem text...",
      className,
      autoFocus = false,
    },
    ref
  ) {
    const mfRef = useRef<any>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [mounted, setMounted] = useState(false);
    const [keyboardActive, setKeyboardActive] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    // Provide methods to parent components via ref
    useImperativeHandle(ref, () => ({
      focus: () => {
        mfRef.current?.focus();
        setIsFocused(true);
      },
      setValue: (val: string) => {
        if (mfRef.current) {
          const cleaned = cleanMinimalMath(val);
          mfRef.current.value = cleaned;
          onChange(cleaned);
          if (cleaned.trim()) {
            setIsFocused(true);
          }
        }
      },
      insert: (latex: string) => {
        if (mfRef.current) {
          mfRef.current.executeCommand(["insert", latex]);
          mfRef.current.focus();
          setIsFocused(true);
        }
      },
      getValue: () => mfRef.current?.value || value,
      showKeyboard: () => {
        const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
        if (mvk) {
          mvk.show({ animate: true });
          setKeyboardActive(true);
        }
        mfRef.current?.focus();
        setIsFocused(true);
      },
      toggleKeyboard: () => {
        toggleVirtualKeyboard();
      },
    }));

    // Dynamic import of MathLive on client side only (safe for SSR)
    useEffect(() => {
      let isMounted = true;
      import("mathlive").then((ml) => {
        if (!isMounted) return;
        if (typeof window !== "undefined") {
          ml.initVirtualKeyboardInCurrentBrowsingContext?.();
        }
        setMounted(true);
      });
      return () => {
        isMounted = false;
      };
    }, []);

    // Auto-close virtual keyboard when clicking outside the field container
    useEffect(() => {
      const handlePointerDown = (e: MouseEvent | TouchEvent) => {
        const target = e.target as Node | null;
        if (!target) return;

        // Keep open if clicked inside our mathfield container
        if (containerRef.current?.contains(target)) return;

        // Keep open if clicked inside the virtual keyboard itself
        const kbdEl = document.querySelector(".ML__keyboard");
        if (kbdEl?.contains(target)) return;

        // Otherwise, user clicked outside - auto close virtual keyboard
        const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
        if (mvk?.visible) {
          mvk.hide({ animate: true });
        }
      };

      document.addEventListener("mousedown", handlePointerDown);
      document.addEventListener("touchstart", handlePointerDown);

      return () => {
        document.removeEventListener("mousedown", handlePointerDown);
        document.removeEventListener("touchstart", handlePointerDown);
      };
    }, []);

    // Auto-close virtual keyboard on component unmount
    useEffect(() => {
      return () => {
        const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
        if (mvk?.visible) {
          mvk.hide({ animate: false });
        }
      };
    }, []);

    // Listen to virtual keyboard toggle/geometry events to keep state in sync
    useEffect(() => {
      if (typeof window === "undefined") return;
      const mvk = (window as any).mathVirtualKeyboard;
      const syncState = () => {
        const currentMvk = (window as any).mathVirtualKeyboard;
        if (currentMvk) {
          setKeyboardActive(Boolean(currentMvk.visible));
        }
      };

      if (mvk) {
        mvk.addEventListener?.("virtual-keyboard-toggle", syncState);
        mvk.addEventListener?.("geometrychange", syncState);
      }
      window.addEventListener?.("virtual-keyboard-toggle", syncState);

      return () => {
        if (mvk) {
          mvk.removeEventListener?.("virtual-keyboard-toggle", syncState);
          mvk.removeEventListener?.("geometrychange", syncState);
        }
        window.removeEventListener?.("virtual-keyboard-toggle", syncState);
      };
    }, [mounted]);

    // Wire up events once mounted
    useEffect(() => {
      if (!mounted) return;
      const mf = mfRef.current;
      if (!mf) return;

      mf.mathVirtualKeyboardPolicy = "manual";
      // Allow pressing Space to insert spaces in math mode without jumping
      mf.mathModeSpace = "\\ ";
      // Strictly minimal math mode - do not switch to text mode
      mf.smartMode = false;
      try {
        mf.menuItems = [];
      } catch {}

      // Disable unselected dark grey and blue highlights inside shadow DOM
      if (mf.shadowRoot) {
        let styleTag = mf.shadowRoot.querySelector("style[data-custom-mathlive]");
        if (!styleTag) {
          styleTag = document.createElement("style");
          styleTag.setAttribute("data-custom-mathlive", "true");
          styleTag.textContent = `
            /* Hide MathLive hamburger menu toggle & built-in buttons */
            .ML__menu-toggle,
            .ML__menu-button,
            [part="menu-toggle"],
            .ML__virtual-keyboard-toggle,
            [part="virtual-keyboard-toggle"] {
              display: none !important;
            }
            /* Hide automatic focused background highlights when unselected */
            .ML__focused .ML__text,
            .ML__text,
            .ML__latex .ML__text {
              background: transparent !important;
            }
            .ML__focused .ML__contains-highlight,
            .ML__contains-highlight {
              background: transparent !important;
            }
            /* Clean, gentle blue tint ONLY when text/math is actively selected */
            .ML__selection {
              background: rgba(59, 130, 246, 0.22) !important;
              border-radius: 3px !important;
            }
            :host(:focus) .ML__selection {
              background: rgba(59, 130, 246, 0.22) !important;
            }
          `;
          mf.shadowRoot.appendChild(styleTag);
        }
      }

      // Sync initial value if provided
      if (value !== undefined && mf.value !== value) {
        mf.value = cleanMinimalMath(value);
      }

      const onInput = () => {
        onChange(mf.value);
      };

      const onBeforeInput = (e: any) => {
        // Disallow Khmer characters from entering the math field
        if (e.data && /[\u1780-\u17FF\u19E0-\u19FF]/.test(e.data)) {
          e.preventDefault?.();
        }
      };

      const onPaste = (e: ClipboardEvent) => {
        const text = e.clipboardData?.getData("text/plain");
        if (text && /[\u1780-\u17FF\u19E0-\u19FF]/.test(text)) {
          e.preventDefault();
          const clean = cleanMinimalMath(text);
          if (clean) {
            mf.executeCommand(["insert", clean]);
            onChange(mf.value);
          }
        }
      };

      const onKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Enter") {
          e.preventDefault();
          // Shift+Enter allows line break for multi-equation systems
          if (e.shiftKey) {
            const currentVal = (mf.value || "").trim();
            if (currentVal) {
              mf.executeCommand(["insert", " \\\\ "]);
              onChange(mf.value);
            }
            return;
          }

          // Enter or Ctrl+Enter / Cmd+Enter submits the problem
          const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
          if (mvk?.visible) {
            mvk.hide({ animate: true });
          }
          if ((mf.value || "").trim()) {
            onSubmit?.();
          }
        }
      };

      const onFocusIn = () => {
        setIsFocused(true);
      };

      const onFocusOut = (e: FocusEvent) => {
        const related = e.relatedTarget as Node | null;
        if (related && containerRef.current?.contains(related)) return;
        const kbdEl = document.querySelector(".ML__keyboard");
        if (related && kbdEl?.contains(related)) return;

        setTimeout(() => {
          const activeEl = document.activeElement;
          if (containerRef.current?.contains(activeEl)) return;
          if (kbdEl?.contains(activeEl)) return;

          setIsFocused(false);

          const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
          if (mvk?.visible) {
            mvk.hide({ animate: true });
          }
        }, 120);
      };

      mf.addEventListener("input", onInput);
      mf.addEventListener("beforeinput", onBeforeInput);
      mf.addEventListener("paste", onPaste);
      mf.addEventListener("keydown", onKeyDown);
      mf.addEventListener("focusin", onFocusIn);
      mf.addEventListener("focus", onFocusIn);
      mf.addEventListener("focusout", onFocusOut);
      mf.addEventListener("blur", onFocusOut);

      if (autoFocus) {
        requestAnimationFrame(() => mf.focus());
      }

      return () => {
        mf.removeEventListener("input", onInput);
        mf.removeEventListener("beforeinput", onBeforeInput);
        mf.removeEventListener("paste", onPaste);
        mf.removeEventListener("keydown", onKeyDown);
        mf.removeEventListener("focusin", onFocusIn);
        mf.removeEventListener("focus", onFocusIn);
        mf.removeEventListener("focusout", onFocusOut);
        mf.removeEventListener("blur", onFocusOut);
      };
    }, [mounted]);

    // Sync external value updates
    useEffect(() => {
      const mf = mfRef.current;
      if (mf && value !== undefined && mf.value !== value) {
        mf.value = formatTextAndMathForMathLive(value);
      }
    }, [value]);

    const insertSymbol = (latex: string) => {
      if (mfRef.current) {
        mfRef.current.executeCommand(["insert", latex]);
        mfRef.current.focus();
      } else {
        onChange(value + latex);
      }
    };

    const toggleVirtualKeyboard = (e?: React.MouseEvent) => {
      e?.preventDefault();
      e?.stopPropagation();
      const mf = mfRef.current;
      const mvk = typeof window !== "undefined" ? (window as any).mathVirtualKeyboard : null;
      if (mvk) {
        if (mvk.visible) {
          mvk.hide({ animate: true });
          setKeyboardActive(false);
        } else {
          mvk.show({ animate: true });
          setKeyboardActive(true);
          mf?.focus();
        }
      } else if (mf) {
        mf.executeCommand("toggleVirtualKeyboard");
        mf.focus();
      }
    };

    const handleClear = () => {
      if (mfRef.current) {
        mfRef.current.value = "";
        onChange("");
        mfRef.current.focus();
      } else {
        onChange("");
      }
    };

    const hasContent = Boolean(value && value.trim());
    const isExpanded = isFocused || hasContent;

    return (
      <div
        ref={containerRef}
        onClick={() => {
          if (!isExpanded) {
            mfRef.current?.focus();
            setIsFocused(true);
          }
        }}
        className={cn("w-full transition-all duration-300", className)}
      >
        {/* Collapsible Field Box: Clean, minimal shadow */}
        <div
          className={cn(
            "group relative rounded-[2rem] bg-card border border-border/80 shadow-xs transition-all duration-200 ease-in-out focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/30 focus-within:shadow-sm",
            isExpanded
              ? "flex flex-col justify-between min-h-[115px] p-3.5 sm:p-4"
              : "flex flex-row items-center justify-between min-h-[66px] sm:min-h-[70px] px-4 sm:px-5 py-2.5 sm:py-3 cursor-pointer hover:border-primary/40"
          )}
        >
          {/* Collapsed Left: Virtual keyboard button */}
          {!isExpanded && (
            <button
              type="button"
              onMouseDown={(e) => e.preventDefault()}
              onClick={(e) => {
                toggleVirtualKeyboard(e);
                mfRef.current?.focus();
                setIsFocused(true);
              }}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary transition-all duration-150 active:translate-y-0.5 shadow-xs mr-3"
              title="Toggle Math Virtual Keyboard"
              aria-label="Toggle Math Virtual Keyboard"
            >
              <Keyboard className="h-4.5 w-4.5" />
            </button>
          )}

          {/* MathLive Field: takes full width when expanded, flex-1 when collapsed */}
          <div
            className={cn(
              "font-display font-bold selection:bg-primary/20 transition-all duration-200 relative",
              isExpanded
                ? "w-full min-h-[55px] max-h-[280px] overflow-y-auto no-scrollbar px-1 py-1"
                : "flex-1 min-h-[42px] max-h-[50px] overflow-hidden flex items-center px-1"
            )}
          >
            {/* Hint text when collapsed & empty */}
            {!isExpanded && !hasContent && placeholder && (
              <div className="pointer-events-none absolute inset-0 flex items-center px-2 text-sm sm:text-base font-medium text-muted-foreground/60 select-none truncate font-sans">
                {placeholder}
              </div>
            )}

            {mounted ? (
              <math-field
                ref={mfRef}
                menu-items="none"
                style={{
                  display: "block",
                  width: "100%",
                  minHeight: isExpanded ? "55px" : "40px",
                  background: "transparent",
                  fontSize: isExpanded ? "1.35rem" : "1.2rem",
                  lineHeight: isExpanded ? "1.8" : "1.5",
                  padding: isExpanded ? "4px 8px" : "2px 4px",
                  outline: "none",
                  border: "none",
                  color: "var(--color-foreground)",
                  cursor: "text",
                  "--contains-highlight-background-color": "transparent",
                  "--highlight-text": "transparent",
                  "--text-highlight-background-color": "transparent",
                  "--selection-background-color": "rgba(59, 130, 246, 0.22)",
                  "--selection-color": "var(--color-foreground)",
                } as React.CSSProperties}
              >
                {value}
              </math-field>
            ) : (
              <div className="px-2 py-1 text-sm sm:text-base font-semibold text-muted-foreground whitespace-pre-line">
                {value || placeholder}
              </div>
            )}
          </div>

          {/* Collapsed Right: Compact Cook It button */}
          {!isExpanded && onSubmit && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                mfRef.current?.focus();
                setIsFocused(true);
                if (value.trim()) onSubmit();
              }}
              className={cn(
                mcButton({ size: "sm" }),
                "shrink-0 ml-3 h-10 px-5 text-sm font-bold rounded-full shadow-xs"
              )}
            >
              Cook It <ArrowRight className="h-4 w-4" />
            </button>
          )}

          {/* Expanded Bottom Action Row & Empty Hint */}
          {isExpanded && (
            <div className="flex items-center justify-between gap-3 pt-2 w-full animate-in fade-in duration-200">
                {/* Left: Virtual keyboard button */}
                <button
                  type="button"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={toggleVirtualKeyboard}
                  className={cn(
                    "flex h-11 w-11 shrink-0 items-center justify-center rounded-full transition-all duration-150 active:translate-y-0.5",
                    keyboardActive
                      ? "bg-primary text-primary-foreground shadow-[0_3px_0_0_var(--primary-deep)]"
                    : "bg-primary-soft text-primary hover:bg-primary hover:text-primary-foreground shadow-sm"
                  )}
                  title="Toggle Math Virtual Keyboard"
                  aria-label="Toggle Math Virtual Keyboard"
                >
                  <Keyboard className="h-5 w-5" />
                </button>

                {/* Right: Clear button & Prominent Cook It button */}
                <div className="flex items-center gap-2">
                  {value && (
                    <button
                      type="button"
                      onClick={handleClear}
                      className="flex h-10 w-10 items-center justify-center rounded-full text-muted-foreground transition hover:bg-destructive/10 hover:text-destructive"
                      title="Clear problem"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}

                  {onSubmit && (
                    <button
                      type="button"
                      onClick={() => {
                        const mvk =
                          typeof window !== "undefined"
                            ? (window as any).mathVirtualKeyboard
                            : null;
                        if (mvk?.visible) {
                          mvk.hide({ animate: true });
                        }
                        onSubmit();
                      }}
                      className={cn(
                        mcButton({ size: "lg" }),
                        "shrink-0 shadow-xs hover:shadow-sm px-7 font-bold"
                      )}
                    >
                      Cook It <ArrowRight className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </div>
          )}
        </div>

        {/* Quick Math Symbols Bar: Smoothly expands when active */}
        <div
          className={cn(
            "flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar pt-1 transition-all duration-300 ease-in-out",
            isExpanded
              ? "max-h-16 opacity-100 mt-2"
              : "max-h-0 opacity-0 overflow-hidden pointer-events-none mt-0"
          )}
        >
          <div className="flex items-center gap-1.5 px-1">
            {MATH_SYMBOLS.map((s, idx) => (
              <button
                key={idx}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => insertSymbol(s.latex)}
                title={s.desc}
                className="flex h-9 shrink-0 items-center justify-center rounded-full border border-border/80 bg-card px-3.5 font-display text-sm font-bold text-foreground shadow-sm transition-all duration-150 hover:-translate-y-0.5 hover:border-primary/60 hover:bg-primary-soft hover:text-primary active:translate-y-0"
              >
                <MathView math={s.label} className="pointer-events-none scale-95" />
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }
);
