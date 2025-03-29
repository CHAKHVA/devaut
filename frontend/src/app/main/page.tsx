import { Button } from "@/components/ui/button";
import { Separator } from "@radix-ui/react-separator";
import { Info, Image as ImageIcon } from "lucide-react"; // Import icons

export default function HomePage() {
  const features = [
    {
      title: "AI Roadmaps",
      description:
        "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story.",
    },
    {
      title: "Gamified Learning",
      description:
        "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story.",
    },
    {
      title: "AI Quizzes",
      description:
        "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story.",
    },
    {
      title: "Personalized Goals",
      description:
        "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story.",
    },
    {
      title: "Interactive Guides",
      description:
        "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story.",
    },
    {
      title: "Community Support",
      description:
        "Body text for whatever you'd like to say. Add main takeaway points, quotes, anecdotes, or even a very very short story.",
    },
  ];

  return (
    <>
      {/* Hero Section */}
      <section className="w-full py-20 md:py-32 lg:py-40 bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-800 relative overflow-hidden">
        {/* Optional: Subtle background pattern like the wireframe */}
        <div
          aria-hidden="true"
          className="absolute inset-0 grid grid-cols-10 grid-rows-10 gap-px opacity-10 dark:opacity-5"
        >
          {[...Array(100)].map((_, i) => (
            <div key={i} className="bg-gray-200 dark:bg-gray-700"></div>
          ))}
        </div>

        <div className="container mx-auto px-4 md:px-6 text-center relative z-10">
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl text-gray-900 dark:text-gray-50">
            Welcome to DevAut
          </h1>
          <p className="mt-4 max-w-[700px] mx-auto text-lg text-gray-600 dark:text-gray-400 md:text-xl">
            Subtitle explaining the core value proposition quickly. Personalized
            AI learning paths.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
            <Button size="lg" variant="secondary">
              Explore Roadmaps
            </Button>
            <Button size="lg">Get Started</Button>
          </div>
        </div>
      </section>
      {/* Placeholder Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-white dark:bg-gray-950">
        <div className="container mx-auto px-4 md:px-6 grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12">
          <div className="flex items-center justify-center aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg">
            <ImageIcon className="h-16 w-16 text-gray-400 dark:text-gray-600" />
          </div>
          <div className="flex items-center justify-center aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg">
            <ImageIcon className="h-16 w-16 text-gray-400 dark:text-gray-600" />
          </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-left mb-8 md:mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl text-gray-900 dark:text-gray-50">
              Heading
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400 md:text-lg">
              Subheading describing this features section.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-12">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">
                  <Info className="h-6 w-6 text-primary" />{" "}
                  {/* Use primary color */}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-50">
                    {feature.title}
                  </h3>
                  <p className="mt-1 text-gray-600 dark:text-gray-400">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      <Separator className="my-12" /> {/* Optional Separator */}
    </>
  );
}
