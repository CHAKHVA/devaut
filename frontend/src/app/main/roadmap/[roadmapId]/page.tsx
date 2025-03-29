import { RoadmapTree } from "@/components/core/RoadmapTree";
// import { AiChatInterface } from "@/components/core/AiChatInterface"; // <-- Removed this import
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { MessageSquare } from "lucide-react";

type RoadmapData = any;
// TODO: Implement data fetching (Server Component or Client Component with useEffect/SWR)
async function getRoadmapData(roadmapId: string): Promise<RoadmapData | null> {
  console.log(`Fetching data for roadmap: ${roadmapId}`);
  // Replace with actual API call to your FastAPI backend
  // Example: const res = await fetch(`/api/roadmaps/${roadmapId}`); const data = await res.json(); return data;

  if (roadmapId === "ai-software") {
    return {
      id: "ai-software",
      title: "AI Software Development",
      description: "Build and deploy machine learning models.",
      steps: [
        {
          id: "intro-ml",
          title: "Introduction to Machine Learning",
          type: "lesson",
          status: "completed",
          children: [],
        },
        {
          id: "python-data",
          title: "Python for Data Science",
          type: "module",
          status: "unlocked",
          children: [
            {
              id: "numpy",
              title: "NumPy Basics",
              type: "lesson",
              status: "locked",
              children: [],
            },
            {
              id: "pandas",
              title: "Pandas DataFrames",
              type: "lesson",
              status: "locked",
              children: [],
            },
          ],
        },
        {
          id: "basic-quiz",
          title: "Fundamentals Quiz",
          type: "quiz",
          status: "locked",
          children: [],
        },
        {
          id: "linear-reg",
          title: "Linear Regression Project",
          type: "assignment",
          status: "locked",
          children: [],
        },
        // Add more steps...
      ],
    };
  }
  return null; // Roadmap not found
}

export default async function RoadmapPage({
  params,
}: {
  params: { roadmapId: string };
}) {
  const roadmapData = await getRoadmapData(params.roadmapId);

  if (!roadmapData) {
    return (
      <div className="container mx-auto px-4 md:px-6 py-12 md:py-24 lg:py-32 text-center">
        <Alert variant="destructive">
          <Terminal className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Roadmap not found or failed to load. Please check the ID or try
            again later.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 md:px-6 py-8 md:py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl">
          {roadmapData.title}
        </h1>
        <p className="text-muted-foreground mt-2">{roadmapData.description}</p>
        {/* TODO: Add progress indicator here */}
      </div>

      {/* AI Chat Area Trigger (Mobile) - Sheet remains, content is empty */}
      <Sheet>
        <SheetTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="fixed bottom-4 right-4 z-50 md:hidden rounded-full p-3 h-auto shadow-lg"
          >
            <MessageSquare className="h-6 w-6" />
            <span className="sr-only">Open Helper</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="bottom" className="h-[75vh] flex flex-col">
          {/* */}
          {/* You could put placeholder text/content here if needed */}
          <p className="text-center text-muted-foreground p-4">
            AI Helper is currently unavailable.
          </p>
        </SheetContent>
      </Sheet>

      {/* Main Content Area (Roadmap + Desktop Chat Panel Space) */}
      <div className="flex flex-col md:flex-row gap-8">
        {/* Roadmap Tree View */}
        <div className="flex-grow">
          {/* TODO: Pass actual fetched roadmap structure */}
          <RoadmapTree data={roadmapData.steps} />
        </div>

        {/* AI Chat Panel Space (Desktop) - Aside remains, content is empty */}
        <aside className="hidden md:block md:w-1/3 lg:w-1/4 sticky top-[80px] h-[calc(100vh-100px)] border-l pl-4">
          {/* <AiChatInterface roadmapId={params.roadmapId} /> <-- Removed AI Chat Component */}
          {/* You could put placeholder text/content here if needed */}
          <p className="text-center text-muted-foreground p-4">
            AI Helper Panel
          </p>
        </aside>
      </div>
    </div>
  );
}
