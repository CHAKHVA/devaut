// components/core/StreakTracker.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Flame } from "lucide-react"; // Example Icon

interface StreakTrackerProps {
  streak: number; // Days
}

export function StreakTracker({ streak }: StreakTrackerProps) {
  const currentStreak = streak ?? 0; // Handle potential null/undefined

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Daily Streak</CardTitle>
        <Flame
          className={`h-4 w-4 ${
            currentStreak > 0 ? "text-orange-500" : "text-muted-foreground"
          }`}
        />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {currentStreak} {currentStreak === 1 ? "Day" : "Days"}
        </div>
        <p className="text-xs text-muted-foreground">
          {currentStreak > 0
            ? "Keep the flame alive!"
            : "Complete a lesson today!"}
        </p>
      </CardContent>
    </Card>
  );
}
