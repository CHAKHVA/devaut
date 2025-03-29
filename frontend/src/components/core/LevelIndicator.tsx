// components/core/LevelIndicator.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress"; // Ensure Progress is imported
import { Star } from "lucide-react"; // Example Icon

interface LevelIndicatorProps {
  level: string;
  progress: number; // Percentage (0-100) towards next level
}

export function LevelIndicator({ level, progress }: LevelIndicatorProps) {
  const currentProgress = progress ?? 0; // Handle potential null/undefined

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Current Level</CardTitle>
        <Star className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{level ?? "N/A"}</div>
        <Progress value={currentProgress} className="mt-2 h-2" />
        <p className="text-xs text-muted-foreground mt-1">
          {currentProgress}% to next level
        </p>
      </CardContent>
    </Card>
  );
}
