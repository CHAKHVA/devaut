// app/(main)/courses/page.tsx
import { CourseCard } from "@/components/core/CourseCard"; // Assuming this component exists
import { Button } from "@/components/ui/button";
import Link from "next/link";

// TODO: Fetch actual course/roadmap data from API
const availableRoadmaps = [
  {
    id: "data-software",
    title: "Data Software Engineering",
    description: "Learn backend systems, databases, and pipelines for data.",
    tags: ["Python", "SQL", "Cloud"],
    difficulty: "Intermediate",
  },
  {
    id: "ai-software",
    title: "AI Software Development",
    description:
      "Build and deploy machine learning models and AI applications.",
    tags: ["Python", "ML", "PyTorch", "Deployment"],
    difficulty: "Advanced",
  },
  {
    id: "game-dev",
    title: "Game Development Fundamentals",
    description: "Create your first games using popular engines and C#.",
    tags: ["Unity", "C#", "Game Design"],
    difficulty: "Beginner",
  },
  {
    id: "web-dev-pro",
    title: "Full-Stack Web Development Pro",
    description:
      "Master frontend and backend technologies for modern web apps.",
    tags: ["React", "Node.js", "Databases", "Next.js"],
    difficulty: "Intermediate",
  },
];

export default function CoursesPage() {
  return (
    <div className="container mx-auto px-4 md:px-6 py-12 md:py-16 lg:py-20">
      <div className="mb-8 md:mb-12 flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl">
          Explore Learning Roadmaps
        </h1>
        {/* Optional: Add filtering/sorting controls here */}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
        {availableRoadmaps.map((roadmap) => (
          <CourseCard key={roadmap.id} roadmap={roadmap} />
        ))}
        {/* Placeholder for when no roadmaps are found */}
        {availableRoadmaps.length === 0 && (
          <p className="col-span-full text-center text-muted-foreground">
            No roadmaps available yet. Check back soon!
          </p>
        )}
      </div>
      {/* Optional: Add pagination if there are many courses */}
    </div>
  );
}
