import { createFileRoute } from "@tanstack/react-router";
import { CookHome } from "@/components/app/CookHome";
import { pageMeta } from "@/lib/mathcook/meta";

export const Route = createFileRoute("/app/solve/")({
  head: () => pageMeta("Solve — MathCook", "Upload a worksheet, type or paste a math problem and MathCook explains it step by step."),
  component: CookHome,
});
