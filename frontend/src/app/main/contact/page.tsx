// Example: app/(main)/dashboard/badges/page.tsx
import { BadgeDisplay } from "@/components/core/BadgeDisplay";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// TODO: Fetch all user badges
async function getUserBadges() {
  return [
    {
      id: "b1",
      name: "Python Padawan",
      iconUrl: "/icons/python-badge.svg",
      description: "Completed first Python module",
      earnedDate: "2024-01-15",
    },
    {
      id: "b2",
      name: "Quiz Whiz",
      iconUrl: "/icons/quiz-badge.svg",
      description: "Achieved 90%+ on 3 quizzes",
      earnedDate: "2024-01-20",
    },
    {
      id: "b3",
      name: "Git Guru",
      iconUrl: "/icons/git-badge.svg",
      description: "Mastered Git basics",
      earnedDate: "2024-02-01",
    },
  ];
}

export default async function BadgesPage() {
  const badges = await getUserBadges();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">My Badges</h2>
        <p className="text-muted-foreground">
          Your collection of achievements.
        </p>
      </div>
      <Card>
        <CardContent className="pt-6">
          {badges.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 md:gap-6">
              {badges.map((badge) => (
                <BadgeDisplay key={badge.id} badge={badge} showDetails />
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              You haven't earned any badges yet. Start a roadmap to begin!
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
