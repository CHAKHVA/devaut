// app/(main)/about/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 md:px-6 py-12 md:py-24 lg:py-32">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl font-bold tracking-tighter sm:text-4xl">
            About DevAut
          </CardTitle>
        </CardHeader>
        <CardContent className="prose dark:prose-invert max-w-none">
          <p>
            Welcome to DevAut, your personalized AI-powered learning companion
            for mastering the world of software development.
          </p>
          <h2>Our Mission</h2>
          <p>
            To provide adaptive, engaging, and effective learning roadmaps
            tailored to individual goals and progress, making complex topics
            like AI, Game Development, and Data Software accessible to everyone.
          </p>
          {/* TODO: Add more content about the platform, team, vision, etc. */}
          <p>
            More details about the platform's features, the technology behind
            it, and the team will go here. We leverage cutting-edge AI to
            generate dynamic content, quizzes, and feedback, ensuring your
            learning journey is always relevant and challenging.
          </p>
          <h2>Key Features (Placeholder)</h2>
          <ul>
            <li>AI-Generated Roadmaps</li>
            <li>Gamified Progress Tracking</li>
            <li>Interactive Quizzes & Assignments</li>
            <li>AI-Powered Q&A</li>
            <li>Community & Peer Review</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
