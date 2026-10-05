import { createFileRoute } from "@tanstack/react-router";
import { Navbar } from "@/components/mathcook/Navbar";
import { HeroSection } from "@/components/mathcook/HeroSection";
import { ProblemInput } from "@/components/mathcook/ProblemInput";
import {
  HowItWorks,
  ProblemUnderstanding,
  SolutionPreview,
  TopicGrid,
  PainPointCards,
  FinalCTA,
  Footer,
} from "@/components/mathcook/Sections";

const TITLE = "MathCook — Cook Any Math Problem";
const DESC =
  "Turn confusing math problems into clear, step-by-step solutions you can actually understand. Upload a worksheet or type a problem.";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: TITLE },
      { name: "description", content: DESC },
      { property: "og:title", content: TITLE },
      { property: "og:description", content: DESC },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <HeroSection />
        <ProblemInput />
        <HowItWorks />
        <ProblemUnderstanding />
        <SolutionPreview />
        <TopicGrid />
        <PainPointCards />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}
