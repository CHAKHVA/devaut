// components/core/PointsCounter.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Award } from "lucide-react"; // Example Icon

interface PointsCounterProps {
  points: number;
}

export function PointsCounter({ points }: PointsCounterProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Total Points</CardTitle>
        <Award className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {points?.toLocaleString() ?? 0}
        </div>{" "}
        {/* Handle potential null/undefined */}
        <p className="text-xs text-muted-foreground">
          Earned across all activities
        </p>
      </CardContent>
    </Card>
  );
}
