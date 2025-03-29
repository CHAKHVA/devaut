// app/(main)/dashboard/page.tsx
import { PointsCounter } from "@/components/core/PointsCounter";
import { LevelIndicator } from "@/components/core/LevelIndicator";
import { StreakTracker } from "@/components/core/StreakTracker";
import { BadgeDisplay } from "@/components/core/BadgeDisplay";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import Link from "next/link";
import { Button } from "@/components/ui/button";

// TODO: Fetch user dashboard data
async function getUserDashboardData() {
  // Replace with actual API call
  return {
    username: "CodeWizard_42",
    points: 1250,
    level: "Intermediate",
    levelProgress: 65, // Percentage towards next level
    dailyStreak: 5,
    recentBadges: [
      {
        id: "b1",
        name: "Python Padawan",
        iconUrl: "/icons/python-badge.svg",
        description: "Completed first Python module",
      },
      {
        id: "b2",
        name: "Quiz Whiz",
        iconUrl: "/icons/quiz-badge.svg",
        description: "Achieved 90%+ on 3 quizzes",
      },
    ],
    activeRoadmap: {
      id: "ai-software",
      title: "AI Software Development",
      progress: 30, // Percentage
    },
  };
}

export default async function DashboardOverviewPage() {
  const data = await getUserDashboardData();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          Welcome back, {data.username}!
        </h2>
        <p className="text-muted-foreground">Here's your learning summary.</p>
      </div>

      {/* Key Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <PointsCounter points={data.points} />
        <LevelIndicator level={data.level} progress={data.levelProgress} />
        <StreakTracker streak={data.dailyStreak} />
      </div>

      {/* Active Roadmap */}
      {data.activeRoadmap && (
        <Card>
          <CardHeader>
            <CardTitle>Current Roadmap</CardTitle>
            <CardDescription>{data.activeRoadmap.title}</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress
              value={data.activeRoadmap.progress}
              className="w-full mb-2"
            />
            <p className="text-sm text-muted-foreground mb-4">
              {data.activeRoadmap.progress}% complete
            </p>
            <Button asChild size="sm">
              <Link href={`/roadmap/${data.activeRoadmap.id}`}>
                Continue Learning
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Recent Badges */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Badges</CardTitle>
          <Link
            href="/dashboard/badges"
            className="text-sm text-primary hover:underline"
          >
            View All
          </Link>
        </CardHeader>
        <CardContent>
          {data.recentBadges.length > 0 ? (
            <div className="flex flex-wrap gap-4">
              {data.recentBadges.map((badge) => (
                <BadgeDisplay key={badge.id} badge={badge} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No badges earned yet. Keep learning!
            </p>
          )}
        </CardContent>
      </Card>

      {/* TODO: Add Recent Activity Section */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Activity feed coming soon...
          </p>
          {/* List recent completions, quiz attempts etc. */}
        </CardContent>
      </Card>
    </div>
  );
}
